#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from soup_files import File

from convert_stream.models import ABCImageObject, ABCPagePdf
from convert_stream.imagelib import ImageObject, LibraryImage
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


#########################################################################
# Converter IMAGEM para Arquivo ou página PDF.
#########################################################################


class ImplementImageConvertPdfFitz(ABCImageConvertPdf):
    """
        Implementação para converter imagens em PDF.
    """
    def __init__(
            self,
            library_image, *,
            progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library_image, progress_bar=progress_bar)
        self._library_pdf = LibraryPDF.FITZ
        
    def from_image_file(self, file: File) -> PageDocumentPdf:
        # https://pymupdf.readthedocs.io/en/latest/recipes-images.html
        doc = fitz.Document()
        img_document: fitz.Document = fitz.Document(file.absolute())  # open pic as document
        rect = img_document[0].rect  # pic dimension
        pdfbytes = img_document.convert_to_pdf()  # make a PDF stream
        img_document.close()  # no longer needed
        image_doc_pdf = fitz.Document("pdf", pdfbytes)  # open stream as PDF
        
        page = doc.new_page(
                    width=rect.width,  # new page with ...
                    height=rect.height # pic dimension
            )  
        page.show_pdf_page(rect, image_doc_pdf, 0)  # image fills the page
        return PageDocumentPdf.create_from_page_fitz(page)
        
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        return self.from_image_bytes(img.to_bytes())
    
    def from_image_bytes(self, image_bytes: bytes) -> PageDocumentPdf:
        doc: fitz.Document = fitz.Document()
        
        # Criar um Pixmap diretamente dos bytes da imagem
        pix = fitz.Pixmap(BytesIO(image_bytes))

        # Criar uma nova página do tamanho da imagem
        page = doc.new_page(width=pix.width, height=pix.height)

        # Inserir a imagem na página
        page.insert_image(page.rect, pixmap=pix)
        return PageDocumentPdf.create_from_page_fitz(page)


class ImplementImageConvertPdfCanvas(ABCImageConvertPdf):
    """
        Implementação para converter uma imagem em página PDF (canvas).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self._library_pdf = LibraryPDF.FITZ
        
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        # Cria um buffer de memória para o PDF
        buffer_pdf = BytesIO()

        # Cria o canvas associado ao buffer
        c: Canvas = canvas.Canvas(buffer_pdf, pagesize=letter)
        # Adicionar a imagem.
        c.drawImage(
                ImageReader(img.to_image_pil()), 
                0, 
                0, 
                width=letter[0], 
                height=letter[1], 
                preserveAspectRatio=True, 
                anchor='c'
            )
        c.showPage()
    
        # Finaliza o PDF
        c.save()

        # Move o ponteiro do buffer para o início
        buffer_pdf.seek(0)

        # Obtém os bytes do PDF
        pdf_bytes = buffer_pdf.getvalue()

        # Fecha o buffer (opcional, mas recomendado)
        buffer_pdf.close()
        
        # Gerar a página PDF
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
        
    def from_image_file(self, file:File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        img = ImageObject.create_from_file(file, library=self.library_image)
        return self.from_image(img)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        return self.from_image(
                ImageObject.create_from_bytes(img_bytes, library=self.library_image)
            )


class ImplementImageConvertToPdfPIL(ABCImageConvertPdf):
    """
        Implementação para converter uma imagem em página PDF (PIL).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self._library_pdf: LibraryPDF = LibraryPDF.FITZ
        
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        img_pil = img.to_image_pil()
        buff = BytesIO()
        # Converter e salvar como PDF
        img_pil.save(buff, "PDF")
        pdf_bytes: bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
        
    def from_image_file(self, file: File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        # Carregar a imagem
        imagem:Image.Image = Image.open(file.absolute())
        buff = BytesIO()
        # Converter e salvar como PDF
        imagem.save(buff, "PDF")
        pdf_bytes: bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        img_pil = Image.open(BytesIO(img_bytes))
        buff_pdf = BytesIO()
        # Converter e salvar como PDF
        img_pil.save(buff_pdf, "PDF")
        pdf_bytes: bytes = buff_pdf.getvalue()
        buff_pdf.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=self._library_pdf)
         
         
class ImageConvertPdf(ABCImageConvertPdf):
    """
        Converter Imagem em páginas PDF.
    """
    def __init__(self, convert_image_to_pdf: ABCImageConvertPdf):
        super().__init__(convert_image_to_pdf.library_image)
        self.convert_image_to_pdf: ABCImageConvertPdf = convert_image_to_pdf
            
    def from_image_file(self, file: File) -> PageDocumentPdf:
        return self.convert_image_to_pdf.from_image_file(file)
    
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        if not isinstance(img, ImageObject):
            raise ValueError(f'{__class__.__name__}\nUser: ImageObject(), não {type(img)}')
        return self.convert_image_to_pdf.from_image(img)
    
    def from_image_bytes(self, img_bytes) -> PageDocumentPdf:
        return self.convert_image_to_pdf.from_image_bytes(img_bytes)
    
    @classmethod
    def create_from_pil(cls, library_image:LibraryImage=LibraryImage.OPENCV) -> ImageConvertPdf:
        img_convert: ABCImageConvertPdf = ImplementImageConvertToPdfPIL(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_canvas(
                cls,
                library_image: LibraryImage = LibraryImage.OPENCV
            ) -> ImageConvertPdf:
        img_convert = ImplementImageConvertPdfCanvas(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_fitz(
                cls,
                library_image: LibraryImage = LibraryImage.OPENCV
            ) -> ImageConvertPdf:
        img_convert = ImplementImageConvertPdfFitz(library_image)
        return cls(img_convert)


