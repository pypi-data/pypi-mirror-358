import copy
import io
import logging
import os
import re
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)

import pdfplumber
from PIL import Image
from tqdm.auto import tqdm
import weakref

from natural_pdf.analyzers.layout.layout_manager import LayoutManager
from natural_pdf.classification.manager import ClassificationError
from natural_pdf.classification.mixin import ClassificationMixin
from natural_pdf.classification.results import ClassificationResult
from natural_pdf.core.highlighting_service import HighlightingService
from natural_pdf.elements.base import Element
from natural_pdf.elements.region import Region
from natural_pdf.export.mixin import ExportMixin
from natural_pdf.extraction.manager import StructuredDataManager
from natural_pdf.extraction.mixin import ExtractionMixin
from natural_pdf.ocr import OCRManager, OCROptions
from natural_pdf.selectors.parser import parse_selector
from natural_pdf.utils.locks import pdf_render_lock

try:
    from typing import Any as TypingAny

    from natural_pdf.search import (
        BaseSearchOptions,
        SearchOptions,
        SearchServiceProtocol,
        TextSearchOptions,
        get_search_service,
    )
except ImportError:
    SearchServiceProtocol = object
    SearchOptions, TextSearchOptions, BaseSearchOptions = object, object, object
    TypingAny = object

    def get_search_service(**kwargs) -> SearchServiceProtocol:
        raise ImportError(
            "Search dependencies are not installed. Install with: pip install natural-pdf[search]"
        )


try:
    from natural_pdf.exporters.searchable_pdf import create_searchable_pdf
except ImportError:
    create_searchable_pdf = None
try:
    from natural_pdf.exporters.original_pdf import create_original_pdf
except ImportError:
    create_original_pdf = None

logger = logging.getLogger("natural_pdf.core.pdf")

def _get_classification_manager_class():
    """Lazy import for ClassificationManager."""
    from natural_pdf.classification.manager import ClassificationManager
    return ClassificationManager

DEFAULT_MANAGERS = {
    "classification": _get_classification_manager_class,
    "structured_data": StructuredDataManager,
}

# Deskew Imports (Conditional)
import numpy as np
from PIL import Image

try:
    import img2pdf
    from deskew import determine_skew

    DESKEW_AVAILABLE = True
except ImportError:
    DESKEW_AVAILABLE = False
    img2pdf = None
# End Deskew Imports

# --- Lazy Page List Helper --- #
from collections.abc import Sequence

class _LazyPageList(Sequence):
    """A lightweight, list-like object that lazily instantiates natural-pdf Page objects.

    The sequence holds `None` placeholders until an index is accessed, at which point
    a real `Page` object is created, cached, and returned.  Slices and iteration are
    also supported and will materialise pages on demand.
    """

    def __init__(self, parent_pdf: "PDF", plumber_pdf: "pdfplumber.PDF", font_attrs=None, load_text=True):
        self._parent_pdf = parent_pdf
        self._plumber_pdf = plumber_pdf
        self._font_attrs = font_attrs
        # One slot per pdfplumber page – initially all None
        self._cache: List[Optional["Page"]] = [None] * len(self._plumber_pdf.pages)
        self._load_text = load_text

    # Internal helper -----------------------------------------------------
    def _create_page(self, index: int) -> "Page":
        cached = self._cache[index]
        if cached is None:
            # Import here to avoid circular import problems
            from natural_pdf.core.page import Page

            plumber_page = self._plumber_pdf.pages[index]
            cached = Page(plumber_page, parent=self._parent_pdf, index=index, font_attrs=self._font_attrs, load_text=self._load_text)
            self._cache[index] = cached
        return cached

    # Sequence protocol ---------------------------------------------------
    def __len__(self) -> int:
        return len(self._cache)

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Materialise pages for slice lazily as well
            indices = range(*key.indices(len(self)))
            return [self._create_page(i) for i in indices]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError("Page index out of range")
            return self._create_page(key)
        else:
            raise TypeError("Page indices must be integers or slices")

    def __iter__(self):
        for i in range(len(self)):
            yield self._create_page(i)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<_LazyPageList(len={len(self)})>"

# --- End Lazy Page List Helper --- #

class PDF(ExtractionMixin, ExportMixin, ClassificationMixin):
    """
    Enhanced PDF wrapper built on top of pdfplumber.

    This class provides a fluent interface for working with PDF documents,
    with improved selection, navigation, and extraction capabilities.
    """

    def __init__(
        self,
        path_or_url_or_stream,
        reading_order: bool = True,
        font_attrs: Optional[List[str]] = None,
        keep_spaces: bool = True,
        text_tolerance: Optional[dict] = None,
        auto_text_tolerance: bool = True,
        text_layer: bool = True,
    ):
        """
        Initialize the enhanced PDF object.

        Args:
            path_or_url_or_stream: Path to the PDF file, a URL, or a file-like object (stream).
            reading_order: Whether to use natural reading order
            font_attrs: Font attributes for grouping characters into words
            keep_spaces: Whether to include spaces in word elements
            text_tolerance: PDFplumber-style tolerance settings
            auto_text_tolerance: Whether to automatically scale text tolerance
            text_layer: Whether to keep the existing text layer from the PDF (default: True).
                       If False, removes all existing text elements during initialization.
        """
        self._original_path_or_stream = path_or_url_or_stream
        self._temp_file = None
        self._resolved_path = None
        self._is_stream = False
        self._text_layer = text_layer
        stream_to_open = None

        if hasattr(path_or_url_or_stream, "read"):  # Check if it's file-like
            logger.info("Initializing PDF from in-memory stream.")
            self._is_stream = True
            self._resolved_path = None  # No resolved file path for streams
            self.source_path = "<stream>"  # Identifier for source
            self.path = self.source_path  # Use source identifier as path for streams
            stream_to_open = path_or_url_or_stream
            try:
                if hasattr(path_or_url_or_stream, "read"):
                    # If caller provided an in-memory binary stream, capture bytes for potential re-export
                    current_pos = path_or_url_or_stream.tell()
                    path_or_url_or_stream.seek(0)
                    self._original_bytes = path_or_url_or_stream.read()
                    path_or_url_or_stream.seek(current_pos)
            except Exception:
                pass
        elif isinstance(path_or_url_or_stream, (str, Path)):
            path_or_url = str(path_or_url_or_stream)
            self.source_path = path_or_url  # Store original path/URL as source
            is_url = path_or_url.startswith("http://") or path_or_url.startswith("https://")

            if is_url:
                logger.info(f"Downloading PDF from URL: {path_or_url}")
                try:
                    with urllib.request.urlopen(path_or_url) as response:
                        data = response.read()
                    # Load directly into an in-memory buffer — no temp file needed
                    buffer = io.BytesIO(data)
                    buffer.seek(0)
                    self._temp_file = None  # No on-disk temp file
                    self._resolved_path = path_or_url  # For repr / get_id purposes
                    stream_to_open = buffer  # pdfplumber accepts file-like objects
                except Exception as e:
                    logger.error(f"Failed to download PDF from URL: {e}")
                    raise ValueError(f"Failed to download PDF from URL: {e}")
            else:
                self._resolved_path = str(Path(path_or_url).resolve())  # Resolve local paths
                stream_to_open = self._resolved_path
            self.path = self._resolved_path  # Use resolved path for file-based PDFs
        else:
            raise TypeError(
                f"Invalid input type: {type(path_or_url_or_stream)}. "
                f"Expected path (str/Path), URL (str), or file-like object."
            )

        logger.info(f"Opening PDF source: {self.source_path}")
        logger.debug(
            f"Parameters: reading_order={reading_order}, font_attrs={font_attrs}, keep_spaces={keep_spaces}"
        )

        try:
            self._pdf = pdfplumber.open(stream_to_open)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}", exc_info=True)
            self.close()  # Attempt cleanup if opening fails
            raise IOError(f"Failed to open PDF source: {self.source_path}") from e

        # Store configuration used for initialization
        self._reading_order = reading_order
        self._config = {"keep_spaces": keep_spaces}
        self._font_attrs = font_attrs

        self._ocr_manager = OCRManager() if OCRManager else None
        self._layout_manager = LayoutManager() if LayoutManager else None
        self.highlighter = HighlightingService(self)
        # self._classification_manager_instance = ClassificationManager() # Removed this line
        self._manager_registry = {}

        # Lazily instantiate pages only when accessed
        self._pages = _LazyPageList(self, self._pdf, font_attrs=font_attrs, load_text=self._text_layer)

        self._element_cache = {}
        self._exclusions = []
        self._regions = []

        logger.info(f"PDF '{self.source_path}' initialized with {len(self._pages)} pages.")

        self._initialize_managers()
        self._initialize_highlighter()
        
        # Remove text layer if requested
        if not self._text_layer:
            logger.info("Removing text layer as requested (text_layer=False)")
            # Text layer is not loaded when text_layer=False, so no need to remove
            pass
        
        # Analysis results accessed via self.analyses property (see below)

        # --- Automatic cleanup when object is garbage-collected ---
        self._finalizer = weakref.finalize(
            self,
            PDF._finalize_cleanup,
            self._pdf,
            getattr(self, "_temp_file", None),
            getattr(self, "_is_stream", False),
        )

        # --- Text tolerance settings ------------------------------------
        # Users can pass pdfplumber-style keys (x_tolerance, x_tolerance_ratio,
        # y_tolerance, etc.) via *text_tolerance*.  We also keep a flag that
        # enables automatic tolerance scaling when explicit values are not
        # supplied.
        self._config["auto_text_tolerance"] = bool(auto_text_tolerance)
        if text_tolerance:
            # Only copy recognised primitives (numbers / None); ignore junk.
            allowed = {
                "x_tolerance",
                "x_tolerance_ratio",
                "y_tolerance",
                "keep_blank_chars",  # passthrough convenience
            }
            for k, v in text_tolerance.items():
                if k in allowed:
                    self._config[k] = v

    def _initialize_managers(self):
        """Set up manager factories for lazy instantiation."""
        # Store factories/classes for each manager key
        self._manager_factories = dict(DEFAULT_MANAGERS)
        self._managers = {}  # Will hold instantiated managers

    def get_manager(self, key: str) -> Any:
        """Retrieve a manager instance by its key, instantiating it lazily if needed."""
        # Check if already instantiated
        if key in self._managers:
            manager_instance = self._managers[key]
            if manager_instance is None:
                raise RuntimeError(f"Manager '{key}' failed to initialize previously.")
            return manager_instance

        # Not instantiated yet: get factory/class
        if not hasattr(self, "_manager_factories") or key not in self._manager_factories:
            raise KeyError(
                f"No manager registered for key '{key}'. Available: {list(getattr(self, '_manager_factories', {}).keys())}"
            )
        factory_or_class = self._manager_factories[key]
        try:
            resolved = factory_or_class
            # If it's a callable that's not a class, call it to get the class/instance
            if not isinstance(resolved, type) and callable(resolved):
                resolved = resolved()
            # If it's a class, instantiate it
            if isinstance(resolved, type):
                instance = resolved()
            else:
                instance = resolved  # Already an instance
            self._managers[key] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to initialize manager for key '{key}': {e}")
            self._managers[key] = None
            raise RuntimeError(f"Manager '{key}' failed to initialize: {e}") from e

    def _initialize_highlighter(self):
        pass

    @property
    def metadata(self) -> Dict[str, Any]:
        """Access metadata as a dictionary."""
        return self._pdf.metadata

    @property
    def pages(self) -> "PageCollection":
        """Access pages as a PageCollection object."""
        from natural_pdf.elements.collections import PageCollection

        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")
        return PageCollection(self._pages)

    def clear_exclusions(self) -> "PDF":
        """
        Clear all exclusion functions from the PDF.

        Returns:
            Self for method chaining
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        self._exclusions = []
        for page in self._pages:
            page.clear_exclusions()
        return self

    def add_exclusion(
        self, exclusion_func: Callable[["Page"], Optional["Region"]], label: str = None
    ) -> "PDF":
        """
        Add an exclusion function to the PDF. Text from these regions will be excluded from extraction.

        Args:
            exclusion_func: A function that takes a Page and returns a Region to exclude, or None
            exclusion_func: A function that takes a Page and returns a Region to exclude, or None
            label: Optional label for this exclusion

        Returns:
            Self for method chaining
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        exclusion_data = (exclusion_func, label)
        self._exclusions.append(exclusion_data)

        for page in self._pages:
            page.add_exclusion(exclusion_func, label=label)

        return self

    def apply_ocr(
        self,
        engine: Optional[str] = None,
        languages: Optional[List[str]] = None,
        min_confidence: Optional[float] = None,
        device: Optional[str] = None,
        resolution: Optional[int] = None,
        apply_exclusions: bool = True,
        detect_only: bool = False,
        replace: bool = True,
        options: Optional[Any] = None,
        pages: Optional[Union[Iterable[int], range, slice]] = None,
    ) -> "PDF":
        """
        Applies OCR to specified pages of the PDF using batch processing.

        Args:
            engine: Name of the OCR engine
            languages: List of language codes
            min_confidence: Minimum confidence threshold
            device: Device to run OCR on
            resolution: DPI resolution for page images
            apply_exclusions: Whether to mask excluded areas
            detect_only: If True, only detect text boxes
            replace: Whether to replace existing OCR elements
            options: Engine-specific options
            pages: Page indices to process or None for all pages

        Returns:
            Self for method chaining
        """
        if not self._ocr_manager:
            logger.error("OCRManager not available. Cannot apply OCR.")
            return self

        # Apply global options as defaults, but allow explicit parameters to override
        import natural_pdf

        # Use global OCR options if parameters are not explicitly set
        if engine is None:
            engine = natural_pdf.options.ocr.engine
        if languages is None:
            languages = natural_pdf.options.ocr.languages
        if min_confidence is None:
            min_confidence = natural_pdf.options.ocr.min_confidence
        if device is None:
            pass  # No default device in options.ocr anymore

        thread_id = threading.current_thread().name
        logger.debug(f"[{thread_id}] PDF.apply_ocr starting for {self.path}")

        target_pages = []

        target_pages = []
        if pages is None:
            target_pages = self._pages
        elif isinstance(pages, slice):
            target_pages = self._pages[pages]
        elif hasattr(pages, "__iter__"):
            try:
                target_pages = [self._pages[i] for i in pages]
            except IndexError:
                raise ValueError("Invalid page index provided in 'pages' iterable.")
            except TypeError:
                raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")
        else:
            raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")

        if not target_pages:
            logger.warning("No pages selected for OCR processing.")
            return self

        page_numbers = [p.number for p in target_pages]
        logger.info(f"Applying batch OCR to pages: {page_numbers}...")

        final_resolution = resolution or getattr(self, "_config", {}).get("resolution", 150)
        logger.debug(f"Using OCR image resolution: {final_resolution} DPI")

        images_pil = []
        page_image_map = []
        logger.info(f"[{thread_id}] Rendering {len(target_pages)} pages...")
        failed_page_num = "unknown"
        render_start_time = time.monotonic()

        try:
            for i, page in enumerate(tqdm(target_pages, desc="Rendering pages", leave=False)):
                failed_page_num = page.number
                logger.debug(f"  Rendering page {page.number} (index {page.index})...")
                to_image_kwargs = {
                    "resolution": final_resolution,
                    "include_highlights": False,
                    "exclusions": "mask" if apply_exclusions else None,
                }
                img = page.to_image(**to_image_kwargs)
                if img is None:
                    logger.error(f"  Failed to render page {page.number} to image.")
                    continue
                    continue
                images_pil.append(img)
                page_image_map.append((page, img))
        except Exception as e:
            logger.error(f"Failed to render pages for batch OCR: {e}")
            logger.error(f"Failed to render pages for batch OCR: {e}")
            raise RuntimeError(f"Failed to render page {failed_page_num} for OCR.") from e

        render_end_time = time.monotonic()
        logger.debug(
            f"[{thread_id}] Finished rendering {len(images_pil)} images (Duration: {render_end_time - render_start_time:.2f}s)"
        )
        logger.debug(
            f"[{thread_id}] Finished rendering {len(images_pil)} images (Duration: {render_end_time - render_start_time:.2f}s)"
        )

        if not images_pil or not page_image_map:
            logger.error("No images were successfully rendered for batch OCR.")
            return self

        manager_args = {
            "images": images_pil,
            "engine": engine,
            "languages": languages,
            "min_confidence": min_confidence,
            "min_confidence": min_confidence,
            "device": device,
            "options": options,
            "detect_only": detect_only,
        }
        manager_args = {k: v for k, v in manager_args.items() if v is not None}

        ocr_call_args = {k: v for k, v in manager_args.items() if k != "images"}
        logger.info(f"[{thread_id}] Calling OCR Manager with args: {ocr_call_args}...")
        logger.info(f"[{thread_id}] Calling OCR Manager with args: {ocr_call_args}...")
        ocr_start_time = time.monotonic()

        batch_results = self._ocr_manager.apply_ocr(**manager_args)

        if not isinstance(batch_results, list) or len(batch_results) != len(images_pil):
            logger.error(f"OCR Manager returned unexpected result format or length.")
            return self

        logger.info("OCR Manager batch processing complete.")

        ocr_end_time = time.monotonic()
        logger.debug(
            f"[{thread_id}] OCR processing finished (Duration: {ocr_end_time - ocr_start_time:.2f}s)"
        )

        logger.info("Adding OCR results to respective pages...")
        total_elements_added = 0

        for i, (page, img) in enumerate(page_image_map):
            results_for_page = batch_results[i]
            if not isinstance(results_for_page, list):
                logger.warning(
                    f"Skipping results for page {page.number}: Expected list, got {type(results_for_page)}"
                )
                continue

            logger.debug(f"  Processing {len(results_for_page)} results for page {page.number}...")
            try:
                if manager_args.get("replace", True) and hasattr(page, "_element_mgr"):
                    page._element_mgr.remove_ocr_elements()

                img_scale_x = page.width / img.width if img.width > 0 else 1
                img_scale_y = page.height / img.height if img.height > 0 else 1
                elements = page._element_mgr.create_text_elements_from_ocr(
                    results_for_page, img_scale_x, img_scale_y
                )

                if elements:
                    total_elements_added += len(elements)
                    logger.debug(f"  Added {len(elements)} OCR TextElements to page {page.number}.")
                else:
                    logger.debug(f"  No valid TextElements created for page {page.number}.")
            except Exception as e:
                logger.error(f"  Error adding OCR elements to page {page.number}: {e}")

        logger.info(f"Finished adding OCR results. Total elements added: {total_elements_added}")
        return self

    def add_region(
        self, region_func: Callable[["Page"], Optional["Region"]], name: str = None
    ) -> "PDF":
        """
        Add a region function to the PDF.

        Args:
            region_func: A function that takes a Page and returns a Region, or None
            region_func: A function that takes a Page and returns a Region, or None
            name: Optional name for the region

        Returns:
            Self for method chaining
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        region_data = (region_func, name)
        self._regions.append(region_data)

        for page in self._pages:
            try:
                region_instance = region_func(page)
                if region_instance and isinstance(region_instance, Region):
                    page.add_region(region_instance, name=name, source="named")
                elif region_instance is not None:
                    logger.warning(
                        f"Region function did not return a valid Region for page {page.number}"
                    )
            except Exception as e:
                logger.error(f"Error adding region for page {page.number}: {e}")

        return self

    @overload
    def find(
        self,
        *,
        text: str,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> Optional[Any]: ...

    @overload
    def find(
        self,
        selector: str,
        *,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> Optional[Any]: ...

    def find(
        self,
        selector: Optional[str] = None,
        *,
        text: Optional[str] = None,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> Optional[Any]:
        """
        Find the first element matching the selector OR text content across all pages.

        Provide EITHER `selector` OR `text`, but not both.

        Args:
            selector: CSS-like selector string.
            text: Text content to search for (equivalent to 'text:contains(...)').
            apply_exclusions: Whether to exclude elements in exclusion regions (default: True).
            regex: Whether to use regex for text search (`selector` or `text`) (default: False).
            case: Whether to do case-sensitive text search (`selector` or `text`) (default: True).
            **kwargs: Additional filter parameters.

        Returns:
            Element object or None if not found.
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        if selector is not None and text is not None:
            raise ValueError("Provide either 'selector' or 'text', not both.")
        if selector is None and text is None:
            raise ValueError("Provide either 'selector' or 'text'.")

        # Construct selector if 'text' is provided
        effective_selector = ""
        if text is not None:
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            effective_selector = f'text:contains("{escaped_text}")'
            logger.debug(
                f"Using text shortcut: find(text='{text}') -> find('{effective_selector}')"
            )
        elif selector is not None:
            effective_selector = selector
        else:
            raise ValueError("Internal error: No selector or text provided.")

        selector_obj = parse_selector(effective_selector)

        # Search page by page
        for page in self.pages:
            # Note: _apply_selector is on Page, so we call find directly here
            # We pass the constructed/validated effective_selector
            element = page.find(
                selector=effective_selector,  # Use the processed selector
                apply_exclusions=apply_exclusions,
                regex=regex,  # Pass down flags
                case=case,
                **kwargs,
            )
            if element:
                return element
        return None  # Not found on any page

    @overload
    def find_all(
        self,
        *,
        text: str,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> "ElementCollection": ...

    @overload
    def find_all(
        self,
        selector: str,
        *,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> "ElementCollection": ...

    def find_all(
        self,
        selector: Optional[str] = None,
        *,
        text: Optional[str] = None,
        apply_exclusions: bool = True,
        regex: bool = False,
        case: bool = True,
        **kwargs,
    ) -> "ElementCollection":
        """
        Find all elements matching the selector OR text content across all pages.

        Provide EITHER `selector` OR `text`, but not both.

        Args:
            selector: CSS-like selector string.
            text: Text content to search for (equivalent to 'text:contains(...)').
            apply_exclusions: Whether to exclude elements in exclusion regions (default: True).
            regex: Whether to use regex for text search (`selector` or `text`) (default: False).
            case: Whether to do case-sensitive text search (`selector` or `text`) (default: True).
            **kwargs: Additional filter parameters.

        Returns:
            ElementCollection with matching elements.
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        if selector is not None and text is not None:
            raise ValueError("Provide either 'selector' or 'text', not both.")
        if selector is None and text is None:
            raise ValueError("Provide either 'selector' or 'text'.")

        # Construct selector if 'text' is provided
        effective_selector = ""
        if text is not None:
            escaped_text = text.replace('"', '\\"').replace("'", "\\'")
            effective_selector = f'text:contains("{escaped_text}")'
            logger.debug(
                f"Using text shortcut: find_all(text='{text}') -> find_all('{effective_selector}')"
            )
        elif selector is not None:
            effective_selector = selector
        else:
            raise ValueError("Internal error: No selector or text provided.")

        # Instead of parsing here, let each page parse and apply
        # This avoids parsing the same selector multiple times if not needed
        # selector_obj = parse_selector(effective_selector)

        # kwargs["regex"] = regex # Removed: Already passed explicitly
        # kwargs["case"] = case   # Removed: Already passed explicitly

        all_elements = []
        for page in self.pages:
            # Call page.find_all with the effective selector and flags
            page_elements = page.find_all(
                selector=effective_selector,
                apply_exclusions=apply_exclusions,
                regex=regex,
                case=case,
                **kwargs,
            )
            if page_elements:
                all_elements.extend(page_elements.elements)

        from natural_pdf.elements.collections import ElementCollection

        return ElementCollection(all_elements)

    def extract_text(
        self,
        selector: Optional[str] = None,
        preserve_whitespace=True,
        use_exclusions=True,
        debug_exclusions=False,
        **kwargs,
    ) -> str:
        """
        Extract text from the entire document or matching elements.

        Args:
            selector: Optional selector to filter elements
            preserve_whitespace: Whether to keep blank characters
            use_exclusions: Whether to apply exclusion regions
            debug_exclusions: Whether to output detailed debugging for exclusions
            preserve_whitespace: Whether to keep blank characters
            use_exclusions: Whether to apply exclusion regions
            debug_exclusions: Whether to output detailed debugging for exclusions
            **kwargs: Additional extraction parameters

        Returns:
            Extracted text as string
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        if selector:
            elements = self.find_all(selector, apply_exclusions=use_exclusions, **kwargs)
            return elements.extract_text(preserve_whitespace=preserve_whitespace, **kwargs)

        if debug_exclusions:
            print(f"PDF: Extracting text with exclusions from {len(self.pages)} pages")
            print(f"PDF: Found {len(self._exclusions)} document-level exclusions")

        texts = []
        for page in self.pages:
            texts.append(
                page.extract_text(
                    preserve_whitespace=preserve_whitespace,
                    use_exclusions=use_exclusions,
                    debug_exclusions=debug_exclusions,
                    **kwargs,
                )
            )

        if debug_exclusions:
            print(f"PDF: Combined {len(texts)} pages of text")

        return "\n".join(texts)

    def extract_tables(
        self, selector: Optional[str] = None, merge_across_pages: bool = False, **kwargs
    ) -> List[Any]:
        """
        Extract tables from the document or matching elements.

        Args:
            selector: Optional selector to filter tables
            merge_across_pages: Whether to merge tables that span across pages
            **kwargs: Additional extraction parameters

        Returns:
            List of extracted tables
        """
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not yet initialized.")

        logger.warning("PDF.extract_tables is not fully implemented yet.")
        all_tables = []

        for page in self.pages:
            if hasattr(page, "extract_tables"):
                all_tables.extend(page.extract_tables(**kwargs))
            else:
                logger.debug(f"Page {page.number} does not have extract_tables method.")

        if selector:
            logger.warning("Filtering extracted tables by selector is not implemented.")

        if merge_across_pages:
            logger.warning("Merging tables across pages is not implemented.")

        return all_tables

    def save_searchable(self, output_path: Union[str, "Path"], dpi: int = 300, **kwargs):
        """
        DEPRECATED: Use save_pdf(..., ocr=True) instead.
        Saves the PDF with an OCR text layer, making content searchable.

        Requires optional dependencies. Install with: pip install \"natural-pdf[ocr-export]\"

        Args:
            output_path: Path to save the searchable PDF
            dpi: Resolution for rendering and OCR overlay
            **kwargs: Additional keyword arguments passed to the exporter
        """
        logger.warning(
            "PDF.save_searchable() is deprecated. Use PDF.save_pdf(..., ocr=True) instead."
        )
        if create_searchable_pdf is None:
            raise ImportError(
                "Saving searchable PDF requires 'pikepdf'. "
                'Install with: pip install "natural-pdf[ocr-export]"'
            )
        output_path_str = str(output_path)
        # Call the exporter directly, passing self (the PDF instance)
        create_searchable_pdf(self, output_path_str, dpi=dpi, **kwargs)
        # Logger info is handled within the exporter now
        # logger.info(f"Searchable PDF saved to: {output_path_str}")

    def save_pdf(
        self,
        output_path: Union[str, Path],
        ocr: bool = False,
        original: bool = False,
        dpi: int = 300,
    ):
        """
        Saves the PDF object (all its pages) to a new file.

        Choose one saving mode:
        - `ocr=True`: Creates a new, image-based PDF using OCR results from all pages.
          Text generated during the natural-pdf session becomes searchable,
          but original vector content is lost. Requires 'ocr-export' extras.
        - `original=True`: Saves a copy of the original PDF file this object represents.
          Any OCR results or analyses from the natural-pdf session are NOT included.
          If the PDF was opened from an in-memory buffer, this mode may not be suitable.
          Requires 'ocr-export' extras.

        Args:
            output_path: Path to save the new PDF file.
            ocr: If True, save as a searchable, image-based PDF using OCR data.
            original: If True, save the original source PDF content.
            dpi: Resolution (dots per inch) used only when ocr=True.

        Raises:
            ValueError: If the PDF has no pages, if neither or both 'ocr'
                        and 'original' are True.
            ImportError: If required libraries are not installed for the chosen mode.
            RuntimeError: If an unexpected error occurs during saving.
        """
        if not self.pages:
            raise ValueError("Cannot save an empty PDF object.")

        if not (ocr ^ original):  # XOR: exactly one must be true
            raise ValueError("Exactly one of 'ocr' or 'original' must be True.")

        output_path_obj = Path(output_path)
        output_path_str = str(output_path_obj)

        if ocr:
            has_vector_elements = False
            for page in self.pages:
                if (
                    hasattr(page, "rects")
                    and page.rects
                    or hasattr(page, "lines")
                    and page.lines
                    or hasattr(page, "curves")
                    and page.curves
                    or (
                        hasattr(page, "chars")
                        and any(getattr(el, "source", None) != "ocr" for el in page.chars)
                    )
                    or (
                        hasattr(page, "words")
                        and any(getattr(el, "source", None) != "ocr" for el in page.words)
                    )
                ):
                    has_vector_elements = True
                    break
            if has_vector_elements:
                logger.warning(
                    "Warning: Saving with ocr=True creates an image-based PDF. "
                    "Original vector elements (rects, lines, non-OCR text/chars) "
                    "will not be preserved in the output file."
                )

            logger.info(f"Saving searchable PDF (OCR text layer) to: {output_path_str}")
            try:
                # Delegate to the searchable PDF exporter, passing self (PDF instance)
                create_searchable_pdf(self, output_path_str, dpi=dpi)
            except Exception as e:
                raise RuntimeError(f"Failed to create searchable PDF: {e}") from e

        elif original:
            if create_original_pdf is None:
                raise ImportError(
                    "Saving with original=True requires 'pikepdf'. "
                    'Install with: pip install "natural-pdf[ocr-export]"'
                )

            # Optional: Add warning about losing OCR data similar to PageCollection
            has_ocr_elements = False
            for page in self.pages:
                if hasattr(page, "find_all"):
                    ocr_text_elements = page.find_all("text[source=ocr]")
                    if ocr_text_elements:
                        has_ocr_elements = True
                        break
                elif hasattr(page, "words"):  # Fallback
                    if any(getattr(el, "source", None) == "ocr" for el in page.words):
                        has_ocr_elements = True
                        break
            if has_ocr_elements:
                logger.warning(
                    "Warning: Saving with original=True preserves original page content. "
                    "OCR text generated in this session will not be included in the saved file."
                )

            logger.info(f"Saving original PDF content to: {output_path_str}")
            try:
                # Delegate to the original PDF exporter, passing self (PDF instance)
                create_original_pdf(self, output_path_str)
            except Exception as e:
                # Re-raise exception from exporter
                raise e

    def ask(
        self,
        question: str,
        mode: str = "extractive",
        pages: Union[int, List[int], range] = None,
        min_confidence: float = 0.1,
        model: str = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Ask a question about the document content.

        Args:
            question: Question to ask about the document
            mode: "extractive" to extract answer from document, "generative" to generate
            pages: Specific pages to query (default: all pages)
            min_confidence: Minimum confidence threshold for answers
            model: Optional model name for question answering
            **kwargs: Additional parameters passed to the QA engine

        Returns:
            A dictionary containing the answer, confidence, and other metadata
            A dictionary containing the answer, confidence, and other metadata
        """
        from natural_pdf.qa import get_qa_engine

        qa_engine = get_qa_engine() if model is None else get_qa_engine(model_name=model)

        if pages is None:
            target_pages = list(range(len(self.pages)))
        elif isinstance(pages, int):
            target_pages = [pages]
        elif isinstance(pages, (list, range)):
            target_pages = pages
        else:
            raise ValueError(f"Invalid pages parameter: {pages}")

        results = []
        for page_idx in target_pages:
            if 0 <= page_idx < len(self.pages):
                page = self.pages[page_idx]
                page_result = qa_engine.ask_pdf_page(
                    page=page, question=question, min_confidence=min_confidence, **kwargs
                )

                if page_result and page_result.get("found", False):
                    results.append(page_result)

        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        if results:
            return results[0]
        else:
            return {
                "answer": None,
                "confidence": 0.0,
                "found": False,
                "page_num": None,
                "source_elements": [],
            }

    def search_within_index(
        self,
        query: Union[str, Path, Image.Image, "Region"],
        search_service: "SearchServiceProtocol",
        options: Optional["SearchOptions"] = None,
    ) -> List[Dict[str, Any]]:
        """
        Finds relevant documents from this PDF within a search index.
        Finds relevant documents from this PDF within a search index.

        Args:
            query: The search query (text, image path, PIL Image, Region)
            search_service: A pre-configured SearchService instance
            options: Optional SearchOptions to configure the query
            query: The search query (text, image path, PIL Image, Region)
            search_service: A pre-configured SearchService instance
            options: Optional SearchOptions to configure the query

        Returns:
            A list of result dictionaries, sorted by relevance
            A list of result dictionaries, sorted by relevance

        Raises:
            ImportError: If search dependencies are not installed
            ValueError: If search_service is None
            TypeError: If search_service does not conform to the protocol
            FileNotFoundError: If the collection managed by the service does not exist
            RuntimeError: For other search failures
            ImportError: If search dependencies are not installed
            ValueError: If search_service is None
            TypeError: If search_service does not conform to the protocol
            FileNotFoundError: If the collection managed by the service does not exist
            RuntimeError: For other search failures
        """
        if not search_service:
            raise ValueError("A configured SearchServiceProtocol instance must be provided.")

        collection_name = getattr(search_service, "collection_name", "<Unknown Collection>")
        logger.info(
            f"Searching within index '{collection_name}' for content from PDF '{self.path}'"
        )

        service = search_service

        query_input = query
        effective_options = copy.deepcopy(options) if options is not None else TextSearchOptions()

        if isinstance(query, Region):
            logger.debug("Query is a Region object. Extracting text.")
            if not isinstance(effective_options, TextSearchOptions):
                logger.warning(
                    "Querying with Region image requires MultiModalSearchOptions. Falling back to text extraction."
                )
            query_input = query.extract_text()
            if not query_input or query_input.isspace():
                logger.error("Region has no extractable text for query.")
                return []

        # Add filter to scope search to THIS PDF
        # Add filter to scope search to THIS PDF
        pdf_scope_filter = {
            "field": "pdf_path",
            "operator": "eq",
            "value": self.path,
        }
        logger.debug(f"Applying filter to scope search to PDF: {pdf_scope_filter}")

        # Combine with existing filters in options (if any)
        if effective_options.filters:
            logger.debug(f"Combining PDF scope filter with existing filters")
            if (
                isinstance(effective_options.filters, dict)
                and effective_options.filters.get("operator") == "AND"
            ):
                effective_options.filters["conditions"].append(pdf_scope_filter)
            elif isinstance(effective_options.filters, list):
                effective_options.filters = {
                    "operator": "AND",
                    "conditions": effective_options.filters + [pdf_scope_filter],
                }
            elif isinstance(effective_options.filters, dict):
                effective_options.filters = {
                    "operator": "AND",
                    "conditions": [effective_options.filters, pdf_scope_filter],
                }
            else:
                logger.warning(
                    f"Unsupported format for existing filters. Overwriting with PDF scope filter."
                )
                effective_options.filters = pdf_scope_filter
        else:
            effective_options.filters = pdf_scope_filter

        logger.debug(f"Final filters for service search: {effective_options.filters}")

        try:
            results = service.search(
                query=query_input,
                options=effective_options,
            )
            logger.info(f"SearchService returned {len(results)} results from PDF '{self.path}'")
            return results
        except FileNotFoundError as fnf:
            logger.error(f"Search failed: Collection not found. Error: {fnf}")
            raise
            logger.error(f"Search failed: Collection not found. Error: {fnf}")
            raise
        except Exception as e:
            logger.error(f"SearchService search failed: {e}")
            raise RuntimeError(f"Search within index failed. See logs for details.") from e
            logger.error(f"SearchService search failed: {e}")
            raise RuntimeError(f"Search within index failed. See logs for details.") from e

    def export_ocr_correction_task(self, output_zip_path: str, **kwargs):
        """
        Exports OCR results from this PDF into a correction task package.
        Exports OCR results from this PDF into a correction task package.

        Args:
            output_zip_path: The path to save the output zip file
            output_zip_path: The path to save the output zip file
            **kwargs: Additional arguments passed to create_correction_task_package
        """
        try:
            from natural_pdf.utils.packaging import create_correction_task_package

            create_correction_task_package(source=self, output_zip_path=output_zip_path, **kwargs)
        except ImportError:
            logger.error(
                "Failed to import 'create_correction_task_package'. Packaging utility might be missing."
            )
            logger.error(
                "Failed to import 'create_correction_task_package'. Packaging utility might be missing."
            )
        except Exception as e:
            logger.error(f"Failed to export correction task: {e}")
            raise
            logger.error(f"Failed to export correction task: {e}")
            raise

    def correct_ocr(
        self,
        correction_callback: Callable[[Any], Optional[str]],
        pages: Optional[Union[Iterable[int], range, slice]] = None,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[], None]] = None,
    ) -> "PDF":
        """
        Applies corrections to OCR text elements using a callback function.
        Applies corrections to OCR text elements using a callback function.

        Args:
            correction_callback: Function that takes an element and returns corrected text or None
            correction_callback: Function that takes an element and returns corrected text or None
            pages: Optional page indices/slice to limit the scope of correction
            max_workers: Maximum number of threads to use for parallel execution
            progress_callback: Optional callback function for progress updates
            max_workers: Maximum number of threads to use for parallel execution
            progress_callback: Optional callback function for progress updates

        Returns:
            Self for method chaining
            Self for method chaining
        """
        target_page_indices = []
        target_page_indices = []
        if pages is None:
            target_page_indices = list(range(len(self._pages)))
        elif isinstance(pages, slice):
            target_page_indices = list(range(*pages.indices(len(self._pages))))
        elif hasattr(pages, "__iter__"):
            try:
                target_page_indices = [int(i) for i in pages]
                for idx in target_page_indices:
                    if not (0 <= idx < len(self._pages)):
                        raise IndexError(f"Page index {idx} out of range (0-{len(self._pages)-1}).")
            except (IndexError, TypeError, ValueError) as e:
                raise ValueError(f"Invalid page index in 'pages': {pages}. Error: {e}") from e
                raise ValueError(f"Invalid page index in 'pages': {pages}. Error: {e}") from e
        else:
            raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")
            raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")

        if not target_page_indices:
            logger.warning("No pages selected for OCR correction.")
            return self

        logger.info(f"Starting OCR correction for pages: {target_page_indices}")
        logger.info(f"Starting OCR correction for pages: {target_page_indices}")

        for page_idx in target_page_indices:
            page = self._pages[page_idx]
            try:
                page.correct_ocr(
                    correction_callback=correction_callback,
                    max_workers=max_workers,
                    progress_callback=progress_callback,
                )
            except Exception as e:
                logger.error(f"Error during correct_ocr on page {page_idx}: {e}")
                logger.error(f"Error during correct_ocr on page {page_idx}: {e}")

        logger.info("OCR correction process finished.")
        logger.info("OCR correction process finished.")
        return self

    def __len__(self) -> int:
        """Return the number of pages in the PDF."""
        if not hasattr(self, "_pages"):
            return 0
        return len(self._pages)

    def __getitem__(self, key) -> Union["Page", "PageCollection"]:
        """Access pages by index or slice."""
        if not hasattr(self, "_pages"):
            raise AttributeError("PDF pages not initialized yet.")

        if isinstance(key, slice):
            from natural_pdf.elements.collections import PageCollection

            return PageCollection(self._pages[key])

        if isinstance(key, int):
            if 0 <= key < len(self._pages):
                return self._pages[key]
            else:
                raise IndexError(f"Page index {key} out of range (0-{len(self._pages)-1}).")
        else:
            raise TypeError(f"Page indices must be integers or slices, not {type(key)}.")

    def close(self):
        """Close the underlying PDF file and clean up any temporary files."""
        if hasattr(self, "_pdf") and self._pdf is not None:
            try:
                self._pdf.close()
                logger.debug(f"Closed pdfplumber PDF object for {self.source_path}")
            except Exception as e:
                logger.warning(f"Error closing pdfplumber object: {e}")
            finally:
                self._pdf = None

        if hasattr(self, "_temp_file") and self._temp_file is not None:
            temp_file_path = None
            try:
                if hasattr(self._temp_file, "name") and self._temp_file.name:
                    temp_file_path = self._temp_file.name
                    # Only unlink if it exists and _is_stream is False (meaning WE created it)
                    if not self._is_stream and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        logger.debug(f"Removed temporary PDF file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file '{temp_file_path}': {e}")

        # Cancels the weakref finalizer so we don't double-clean
        if hasattr(self, "_finalizer") and self._finalizer.alive:
            self._finalizer()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """Return a string representation of the PDF object."""
        if not hasattr(self, "_pages"):
            page_count_str = "uninitialized"
        else:
            page_count_str = str(len(self._pages))

        source_info = getattr(self, "source_path", "unknown source")
        return f"<PDF source='{source_info}' pages={page_count_str}>"

    def get_id(self) -> str:
        """Get unique identifier for this PDF."""
        """Get unique identifier for this PDF."""
        return self.path

    # --- Deskew Method --- #

    def deskew(
        self,
        pages: Optional[Union[Iterable[int], range, slice]] = None,
        resolution: int = 300,
        angle: Optional[float] = None,
        detection_resolution: int = 72,
        force_overwrite: bool = False,
        **deskew_kwargs,
    ) -> "PDF":
        """
        Creates a new, in-memory PDF object containing deskewed versions of the
        specified pages from the original PDF.

        This method renders each selected page, detects and corrects skew using the 'deskew'
        library, and then combines the resulting images into a new PDF using 'img2pdf'.
        The new PDF object is returned directly.

        Important: The returned PDF is image-based. Any existing text, OCR results,
        annotations, or other elements from the original pages will *not* be carried over.

        Args:
            pages: Page indices/slice to include (0-based). If None, processes all pages.
            resolution: DPI resolution for rendering the output deskewed pages.
            angle: The specific angle (in degrees) to rotate by. If None, detects automatically.
            detection_resolution: DPI resolution used for skew detection if angles are not
                                  already cached on the page objects.
            force_overwrite: If False (default), raises a ValueError if any target page
                             already contains processed elements (text, OCR, regions) to
                             prevent accidental data loss. Set to True to proceed anyway.
            **deskew_kwargs: Additional keyword arguments passed to `deskew.determine_skew`
                             during automatic detection (e.g., `max_angle`, `num_peaks`).

        Returns:
            A new PDF object representing the deskewed document.

        Raises:
            ImportError: If 'deskew' or 'img2pdf' libraries are not installed.
            ValueError: If `force_overwrite` is False and target pages contain elements.
            FileNotFoundError: If the source PDF cannot be read (if file-based).
            IOError: If creating the in-memory PDF fails.
            RuntimeError: If rendering or deskewing individual pages fails.
        """
        if not DESKEW_AVAILABLE:
            raise ImportError(
                "Deskew/img2pdf libraries missing. Install with: pip install natural-pdf[deskew]"
            )

        target_pages = self._get_target_pages(pages)  # Use helper to resolve pages

        # --- Safety Check --- #
        if not force_overwrite:
            for page in target_pages:
                # Check if the element manager has been initialized and contains any elements
                if (
                    hasattr(page, "_element_mgr")
                    and page._element_mgr
                    and page._element_mgr.has_elements()
                ):
                    raise ValueError(
                        f"Page {page.number} contains existing elements (text, OCR, etc.). "
                        f"Deskewing creates an image-only PDF, discarding these elements. "
                        f"Set force_overwrite=True to proceed."
                    )

        # --- Process Pages --- #
        deskewed_images_bytes = []
        logger.info(f"Deskewing {len(target_pages)} pages (output resolution={resolution} DPI)...")

        for page in tqdm(target_pages, desc="Deskewing Pages", leave=False):
            try:
                # Use page.deskew to get the corrected PIL image
                # Pass down resolutions and kwargs
                deskewed_img = page.deskew(
                    resolution=resolution,
                    angle=angle,  # Let page.deskew handle detection/caching
                    detection_resolution=detection_resolution,
                    **deskew_kwargs,
                )

                if not deskewed_img:
                    logger.warning(
                        f"Page {page.number}: Failed to generate deskewed image, skipping."
                    )
                    continue

                # Convert image to bytes for img2pdf (use PNG for lossless quality)
                with io.BytesIO() as buf:
                    deskewed_img.save(buf, format="PNG")
                    deskewed_images_bytes.append(buf.getvalue())

            except Exception as e:
                logger.error(
                    f"Page {page.number}: Failed during deskewing process: {e}", exc_info=True
                )
                # Option: Raise a runtime error, or continue and skip the page?
                # Raising makes the whole operation fail if one page fails.
                raise RuntimeError(f"Failed to process page {page.number} during deskewing.") from e

        # --- Create PDF --- #
        if not deskewed_images_bytes:
            raise RuntimeError("No pages were successfully processed to create the deskewed PDF.")

        logger.info(f"Combining {len(deskewed_images_bytes)} deskewed images into in-memory PDF...")
        try:
            # Use img2pdf to combine image bytes into PDF bytes
            pdf_bytes = img2pdf.convert(deskewed_images_bytes)

            # Wrap bytes in a stream
            pdf_stream = io.BytesIO(pdf_bytes)

            # Create a new PDF object from the stream using original config
            logger.info("Creating new PDF object from deskewed stream...")
            new_pdf = PDF(
                pdf_stream,
                reading_order=self._reading_order,
                font_attrs=self._font_attrs,
                keep_spaces=self._config.get("keep_spaces", True),
                text_layer=self._text_layer,
            )
            return new_pdf
        except Exception as e:
            logger.error(f"Failed to create in-memory PDF using img2pdf/PDF init: {e}")
            raise IOError("Failed to create deskewed PDF object from image stream.") from e

    # --- End Deskew Method --- #

    # --- Classification Methods --- #

    def classify_pages(
        self,
        labels: List[str],
        model: Optional[str] = None,
        pages: Optional[Union[Iterable[int], range, slice]] = None,
        analysis_key: str = "classification",
        using: Optional[str] = None,
        **kwargs,
    ) -> "PDF":
        """
        Classifies specified pages of the PDF.

        Args:
            labels: List of category names
            model: Model identifier ('text', 'vision', or specific HF ID)
            pages: Page indices, slice, or None for all pages
            analysis_key: Key to store results in page's analyses dict
            using: Processing mode ('text' or 'vision')
            **kwargs: Additional arguments for the ClassificationManager

        Returns:
            Self for method chaining
        """
        if not labels:
            raise ValueError("Labels list cannot be empty.")

        try:
            manager = self.get_manager("classification")
        except (ValueError, RuntimeError) as e:
            raise ClassificationError(f"Cannot get ClassificationManager: {e}") from e

        if not manager or not manager.is_available():
            from natural_pdf.classification.manager import is_classification_available
            
            if not is_classification_available():
                raise ImportError(
                    "Classification dependencies missing. "
                    'Install with: pip install "natural-pdf[ai]"'
                )
            raise ClassificationError("ClassificationManager not available.")

        target_pages = []
        if pages is None:
            target_pages = self._pages
        elif isinstance(pages, slice):
            target_pages = self._pages[pages]
        elif hasattr(pages, "__iter__"):
            try:
                target_pages = [self._pages[i] for i in pages]
            except IndexError:
                raise ValueError("Invalid page index provided.")
            except TypeError:
                raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")
        else:
            raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")

        if not target_pages:
            logger.warning("No pages selected for classification.")
            return self

        inferred_using = manager.infer_using(model if model else manager.DEFAULT_TEXT_MODEL, using)
        logger.info(
            f"Classifying {len(target_pages)} pages using model '{model or '(default)'}' (mode: {inferred_using})"
        )

        page_contents = []
        pages_to_classify = []
        logger.debug(f"Gathering content for {len(target_pages)} pages...")

        for page in target_pages:
            try:
                content = page._get_classification_content(model_type=inferred_using, **kwargs)
                page_contents.append(content)
                pages_to_classify.append(page)
            except ValueError as e:
                logger.warning(f"Skipping page {page.number}: Cannot get content - {e}")
            except Exception as e:
                logger.warning(f"Skipping page {page.number}: Error getting content - {e}")

        if not page_contents:
            logger.warning("No content could be gathered for batch classification.")
            return self

        logger.debug(f"Gathered content for {len(pages_to_classify)} pages.")

        try:
            batch_results = manager.classify_batch(
                item_contents=page_contents,
                labels=labels,
                model_id=model,
                using=inferred_using,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Batch classification failed: {e}")
            raise ClassificationError(f"Batch classification failed: {e}") from e

        if len(batch_results) != len(pages_to_classify):
            logger.error(
                f"Mismatch between number of results ({len(batch_results)}) and pages ({len(pages_to_classify)})"
            )
            return self

        logger.debug(
            f"Distributing {len(batch_results)} results to pages under key '{analysis_key}'..."
        )
        for page, result_obj in zip(pages_to_classify, batch_results):
            try:
                if not hasattr(page, "analyses") or page.analyses is None:
                    page.analyses = {}
                page.analyses[analysis_key] = result_obj
            except Exception as e:
                logger.warning(
                    f"Failed to store classification results for page {page.number}: {e}"
                )

        logger.info(f"Finished classifying PDF pages.")
        return self

    # --- End Classification Methods --- #

    # --- Extraction Support --- #
    def _get_extraction_content(self, using: str = "text", **kwargs) -> Any:
        """
        Retrieves the content for the entire PDF.

        Args:
            using: 'text' or 'vision'
            **kwargs: Additional arguments passed to extract_text or page.to_image

        Returns:
            str: Extracted text if using='text'
            List[PIL.Image.Image]: List of page images if using='vision'
            None: If content cannot be retrieved
        """
        if using == "text":
            try:
                layout = kwargs.pop("layout", True)
                return self.extract_text(layout=layout, **kwargs)
            except Exception as e:
                logger.error(f"Error extracting text from PDF: {e}")
                return None
        elif using == "vision":
            page_images = []
            logger.info(f"Rendering {len(self.pages)} pages to images...")

            resolution = kwargs.pop("resolution", 72)
            include_highlights = kwargs.pop("include_highlights", False)
            labels = kwargs.pop("labels", False)

            try:
                for page in tqdm(self.pages, desc="Rendering Pages"):
                    img = page.to_image(
                        resolution=resolution,
                        include_highlights=include_highlights,
                        labels=labels,
                        **kwargs,
                    )
                    if img:
                        page_images.append(img)
                    else:
                        logger.warning(f"Failed to render page {page.number}, skipping.")
                if not page_images:
                    logger.error("Failed to render any pages.")
                    return None
                return page_images
            except Exception as e:
                logger.error(f"Error rendering pages: {e}")
                return None
        else:
            logger.error(f"Unsupported value for 'using': {using}")
            return None

    # --- End Extraction Support --- #

    def _gather_analysis_data(
        self,
        analysis_keys: List[str],
        include_content: bool,
        include_images: bool,
        image_dir: Optional[Path],
        image_format: str,
        image_resolution: int,
    ) -> List[Dict[str, Any]]:
        """
        Gather analysis data from all pages in the PDF.

        Args:
            analysis_keys: Keys in the analyses dictionary to export
            include_content: Whether to include extracted text
            include_images: Whether to export images
            image_dir: Directory to save images
            image_format: Format to save images
            image_resolution: Resolution for exported images

        Returns:
            List of dictionaries containing analysis data
        """
        if not hasattr(self, "_pages") or not self._pages:
            logger.warning(f"No pages found in PDF {self.path}")
            return []

        all_data = []

        for page in tqdm(self._pages, desc="Gathering page data", leave=False):
            # Basic page information
            page_data = {
                "pdf_path": self.path,
                "page_number": page.number,
                "page_index": page.index,
            }

            # Include extracted text if requested
            if include_content:
                try:
                    page_data["content"] = page.extract_text(preserve_whitespace=True)
                except Exception as e:
                    logger.error(f"Error extracting text from page {page.number}: {e}")
                    page_data["content"] = ""

            # Save image if requested
            if include_images:
                try:
                    # Create image filename
                    image_filename = f"pdf_{Path(self.path).stem}_page_{page.number}.{image_format}"
                    image_path = image_dir / image_filename

                    # Save image
                    page.save_image(
                        str(image_path), resolution=image_resolution, include_highlights=True
                    )

                    # Add relative path to data
                    page_data["image_path"] = str(Path(image_path).relative_to(image_dir.parent))
                except Exception as e:
                    logger.error(f"Error saving image for page {page.number}: {e}")
                    page_data["image_path"] = None

            # Add analyses data
            for key in analysis_keys:
                if not hasattr(page, "analyses") or not page.analyses:
                    raise ValueError(f"Page {page.number} does not have analyses data")

                if key not in page.analyses:
                    raise KeyError(f"Analysis key '{key}' not found in page {page.number}")

                # Get the analysis result
                analysis_result = page.analyses[key]

                # If the result has a to_dict method, use it
                if hasattr(analysis_result, "to_dict"):
                    analysis_data = analysis_result.to_dict()
                else:
                    # Otherwise, use the result directly if it's dict-like
                    try:
                        analysis_data = dict(analysis_result)
                    except (TypeError, ValueError):
                        # Last resort: convert to string
                        analysis_data = {"raw_result": str(analysis_result)}

                # Add analysis data to page data with the key as prefix
                for k, v in analysis_data.items():
                    page_data[f"{key}.{k}"] = v

            all_data.append(page_data)

        return all_data

    def _get_target_pages(
        self, pages: Optional[Union[Iterable[int], range, slice]] = None
    ) -> List["Page"]:
        """
        Helper method to get a list of Page objects based on the input pages.

        Args:
            pages: Page indices, slice, or None for all pages

        Returns:
            List of Page objects
        """
        if pages is None:
            return self._pages
        elif isinstance(pages, slice):
            return self._pages[pages]
        elif hasattr(pages, "__iter__"):
            try:
                return [self._pages[i] for i in pages]
            except IndexError:
                raise ValueError("Invalid page index provided in 'pages' iterable.")
            except TypeError:
                raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")
        else:
            raise TypeError("'pages' must be None, a slice, or an iterable of page indices.")

    # --- Classification Mixin Implementation --- #

    def _get_classification_manager(self) -> "ClassificationManager":
        """Returns the ClassificationManager instance for this PDF."""
        try:
            return self.get_manager("classification")
        except (KeyError, RuntimeError) as e:
            raise AttributeError(f"Could not retrieve ClassificationManager: {e}") from e

    def _get_classification_content(self, model_type: str, **kwargs) -> Union[str, Image.Image]:
        """
        Provides the content for classifying the entire PDF.

        Args:
            model_type: 'text' or 'vision'.
            **kwargs: Additional arguments (e.g., for text extraction or image rendering).

        Returns:
            Extracted text (str) or the first page's image (PIL.Image).

        Raises:
            ValueError: If model_type is 'vision' and PDF has != 1 page,
                      or if model_type is unsupported, or if content cannot be generated.
        """
        if model_type == "text":
            try:
                # Extract text from the whole document
                text = self.extract_text(**kwargs)  # Pass relevant kwargs
                if not text or text.isspace():
                    raise ValueError("PDF contains no extractable text for classification.")
                return text
            except Exception as e:
                logger.error(f"Error extracting text for PDF classification: {e}")
                raise ValueError("Failed to extract text for classification.") from e

        elif model_type == "vision":
            if len(self.pages) == 1:
                # Use the single page's content method
                try:
                    return self.pages[0]._get_classification_content(model_type="vision", **kwargs)
                except Exception as e:
                    logger.error(f"Error getting image from single page for classification: {e}")
                    raise ValueError("Failed to get image from single page.") from e
            elif len(self.pages) == 0:
                raise ValueError("Cannot classify empty PDF using vision model.")
            else:
                raise ValueError(
                    f"Vision classification for a PDF object is only supported for single-page PDFs. "
                    f"This PDF has {len(self.pages)} pages. Use pdf.pages[0].classify() or pdf.classify_pages()."
                )
        else:
            raise ValueError(f"Unsupported model_type for PDF classification: {model_type}")

    # --- End Classification Mixin Implementation ---

    # ------------------------------------------------------------------
    # Unified analysis storage (maps to metadata["analysis"])
    # ------------------------------------------------------------------

    @property
    def analyses(self) -> Dict[str, Any]:
        if not hasattr(self, "metadata") or self.metadata is None:
            # For PDF, metadata property returns self._pdf.metadata which may be None
            self._pdf.metadata = self._pdf.metadata or {}
        if self.metadata is None:
            # Fallback safeguard
            self._pdf.metadata = {}
        return self.metadata.setdefault("analysis", {})  # type: ignore[attr-defined]

    @analyses.setter
    def analyses(self, value: Dict[str, Any]):
        if not hasattr(self, "metadata") or self.metadata is None:
            self._pdf.metadata = self._pdf.metadata or {}
        self.metadata["analysis"] = value  # type: ignore[attr-defined]

    # Static helper for weakref.finalize to avoid capturing 'self'
    @staticmethod
    def _finalize_cleanup(plumber_pdf, temp_file_obj, is_stream):
        try:
            if plumber_pdf is not None:
                plumber_pdf.close()
        except Exception:
            pass

        if temp_file_obj and not is_stream:
            try:
                path = temp_file_obj.name if hasattr(temp_file_obj, "name") else None
                if path and os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file '{path}': {e}")
