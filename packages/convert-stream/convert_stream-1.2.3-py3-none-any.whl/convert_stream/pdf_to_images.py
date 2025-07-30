#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Módulo para converter PDFs em imagens
"""
from __future__ import annotations
from typing import List
from convert_stream.imagelib import ImageObject, LibraryImage
from convert_stream.models import ABCImageObject, ABCPagePdf
from convert_stream.models.models_pdf import ABCConvertPdf, ABCImageConvertPdf, LibraryPDF
from convert_stream.progress.progress_bar import ProgressBarAdapter, ProgressBarSimple
from convert_stream.pdf_page import (
    PageDocumentPdf, MODULE_PYPDF2, MODULE_FITZ
)

if MODULE_PYPDF2:
    from PyPDF2 import PdfReader, PdfWriter, PageObject
if MODULE_FITZ:
    try:
        import fitz
    except:
        try:
            import pymupdf
        except:
            pass

#======================================================================#
# Converter PDFs em Imagens
#======================================================================#


class ImplementPdfToImageFitz(ABCConvertPdf):
    """
        Implementação para converter PDFs em Imagens com o fitz.
    """

    def __init__(
            self,
            library_image: LibraryImage = LibraryImage.OPENCV,
            *,
            dpi: int = 150,
            progress_bar: ProgressBarAdapter(ProgressBarSimple()),
            ):
        """
        :param library_image:
        :param dpi:

        """
        super().__init__(progress_bar=progress_bar)
        self.library_image: LibraryImage = library_image
        self.dpi: int = dpi

    def from_page_bytes(self, page_bytes: bytes, dpi: int = 150) -> ABCImageObject:
        """
            Recebe uma página PDF e converte os bytes da página PDF em ImagemObject
        """
        if not isinstance(page_bytes, bytes):
            raise ValueError(f'{__class__.__name__}\nUse: bytes, não {type(page_bytes)}')
        page_pdf = PageDocumentPdf.create_from_page_bytes(page_bytes, library=LibraryPDF.FITZ)
        pix: fitz.Pixmap = page_pdf.page.page.get_pixmap()
        return ImageObject.create_from_bytes(pix.tobytes(), library=self.library_image)

    def from_page_pdf(self, page: ABCPagePdf, dpi: int = 200) -> ABCImageObject:
        if page.current_library == LibraryPDF.FITZ:
            return self.__from_page_fitz(page.page.page)
        return self.from_page_bytes(page.to_bytes())

    def __from_page_fitz(self, page_fitz: fitz.Page) -> ImageObject:
        """
            Converte uma página PDF fitz em imagem.
        """
        if not isinstance(page_fitz, fitz.Page):
            raise ValueError(f'{__class__.__name__}Use: fitz.Page(), não {type(page_fitz)}')
        #self.pbar.update_text('Convertendo página PDF em imagem')
        pix: fitz.Pixmap = page_fitz.get_pixmap()
        return ImageObject.create_from_bytes(pix.tobytes(), library=self.library_image)

    def inner_images(self, page_bytes) -> List[ImageObject]:
        images_obj: List[ImageObject] = []
        doc = fitz.Document(stream=page_bytes, filetype="pdf")
        page: fitz.Page = doc[0]
        # Extrair imagens embutidas na página
        images_list = page.get_images(full=True)

        for n, img in enumerate(images_list):
            try:
                xref = img[0]  # Referência do objeto da imagem
                base_image = doc.extract_image(xref)  # Extrair imagem
                image_bytes = base_image["image"]  # Bytes da imagem
                image_ext = base_image["ext"]  # Extensão (jpg, png, etc.)
            except Exception as e:
                print(e)
            else:
                img = ImageObject.create_from_bytes(image_bytes, library=self.library_image)
                images_obj.append(img)
        return images_obj


class ConvertPdfToImage(ABCConvertPdf):
    """
        Conversor de PDFs em Imagens.
    """

    def __init__(
                self, *,
                library_pdf: LibraryPDF = LibraryPDF.FITZ,
                library_image: LibraryImage = LibraryImage.OPENCV,
                dpi: int = 150,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple()),
            ):
        super().__init__(progress_bar=progress_bar)
        self.library_pdf: LibraryPDF = library_pdf
        if self.library_pdf == LibraryPDF.FITZ:
            self.convert_pdf_to_images = ImplementPdfToImageFitz(
                library_image, dpi=dpi, progress_bar=progress_bar
            )
        elif self.library_pdf == LibraryPDF.PYPDF:
            raise NotImplementedError(f'{__class__.__name__}\nFuncionalidade não implementada para PYPDF2')
        elif self.library_pdf == LibraryPDF.CANVAS:
            raise NotImplementedError(f'{__class__.__name__}\nFuncionalidade não implementada para CANVAS')
        else:
            raise NotImplementedError(f'{__class__.__name__}\nLibraryPDF inválida: {type(self.library_pdf)}')

    def from_page_bytes(self, page_bytes: bytes, dpi: int = 150) -> ABCImageObject:
        return self.convert_pdf_to_images.from_page_bytes(page_bytes)

    def from_page_pdf(self, page: ABCPagePdf, dpi: int = 150) -> ABCImageObject:
        return self.convert_pdf_to_images.from_page_pdf(page)

    def inner_images(self, page_bytes) -> List[ImageObject]:
        return self.convert_pdf_to_images.inner_images(page_bytes)


