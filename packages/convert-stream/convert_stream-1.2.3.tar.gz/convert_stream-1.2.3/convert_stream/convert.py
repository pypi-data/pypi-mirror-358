#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
import pandas

from convert_stream.models import ABCDocumentStream, LibraryImage, LibraryPDF
from convert_stream.imagelib import ImageObject
from convert_stream.progress.progress_bar import ProgressBarAdapter, ProgressBarSimple
from convert_stream.pdf_page import PageDocumentPdf
from convert_stream.pdf_document import DocumentPdf
from convert_stream.pdf_to_images import ConvertPdfToImage
from convert_stream.image_to_pdf import ImageConvertPdf
from soup_files import File, Directory
 
#==================================================================#
# PDF
#==================================================================#


class PdfStream(ABCDocumentStream):
    """
        Objeto para manipular a exportação de dados PDF    
    """

    def __init__(
                self, *,
                library_pdf: LibraryPDF = LibraryPDF.FITZ,
                library_image: LibraryImage = LibraryImage.OPENCV,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple())
            ):
        super().__init__(library_pdf=library_pdf, library_image=library_image, progress_bar=progress_bar)
        self.num_pages: int = 0
        self.library_pdf: LibraryPDF = library_pdf
        self.library_image: LibraryImage = library_image
        self.document: DocumentPdf = DocumentPdf(self.library_pdf, progress_bar=progress_bar)
        self.convert_pdf_to_images: ConvertPdfToImage = ConvertPdfToImage(
            library_image=library_image, progress_bar=progress_bar
        )
        
        if self.library_pdf == LibraryPDF.CANVAS:
            self.convert_images_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_canvas(self.library_image)
        elif self.library_pdf == LibraryPDF.PILPDF:
            self.convert_images_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_pil(LibraryImage.PIL)
        else:
            self.convert_images_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_fitz(self.library_image)
        
    @property
    def num_pages(self) -> int:
        return self.document.num_pages
    
    @num_pages.setter
    def num_pages(self, num: int):
        pass
        
    @property
    def pages(self) -> List[PageDocumentPdf]:
        return self.document.pages
    
    @pages.setter
    def pages(self, new: List[PageDocumentPdf]):
        if not isinstance(new, list):
            return
        self.document.clear()
        for pg in new:
            self.add_page(pg)
        
    def is_null(self) -> bool:
        return self.document.is_null()
    
    def clear(self):
        self.document.clear()
        
    def add_page(self, p: PageDocumentPdf):
        if not isinstance(p, PageDocumentPdf):
            return
        self.document.add_page(p)
            
    def add_pages(self, pages: List[PageDocumentPdf]):
        if not isinstance(pages, list):
            print(f'{__class__.__name__} Erro: Use lista de PageDocumentPdf, não {type(pages)}')
            return
        max_num: int = len(pages)
        self.progress_bar.start()
        for num, p in enumerate(pages):
            self.progress_bar.update(
                ((num+1)/max_num) * 100,
                f'Adicionando página: [{num+1} de {max_num}]'
            )
            self.add_page(p)
        self.progress_bar.stop()

    def add_page_pdf_bytes(self, bt: bytes):
        _page = PageDocumentPdf.create_from_page_bytes(bt, library=self.library_pdf)
        self.add_page(_page)
            
    def add_file_pdf(self, f: File):
        doc: DocumentPdf = DocumentPdf(self.library_pdf)
        doc.add_file_pdf(f)
        self.add_pages(doc.pages)
        
    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)
            
    def add_document(self, doc:DocumentPdf):
        self.add_pages(doc.pages)
        
    def add_image(self, image: ImageObject):
        pg: PageDocumentPdf = self.convert_images_to_pdf.from_image(image)
        self.add_page(pg)

    def add_images(self, images: List[ImageObject]):
        maxnum: int = len(images)
        self.progress_bar.start()
        for n, img in enumerate(images):
            self.progress_bar.update(
                ((n+1)/maxnum) * 100,
                f'Adicionando imagens ao documento: [{n+1}] de {maxnum}'
            )
            self.add_image(img)
        self.progress_bar.stop()
        
    def to_file_pdf(self, f: File):
        if self.is_null():
            print(
                f'{__class__.__name__} Nenhuma página foi adiconada, adicione páginas ao documento para prosseguir!'
            )
        docpdf: DocumentPdf = DocumentPdf(
            self.library_pdf, progress_bar=self.progress_bar, pages=self.pages
        )
        docpdf.to_file_pdf(f)
        
    def to_files_pdf(self, outdir: Directory, *, prefix='documento-pag'):
        if self.is_null():
            print(
                f'{__class__.__name__} Adicione páginas ao documento para prosseguir!'
            )
            return
        outdir.mkdir()
        _document: DocumentPdf = DocumentPdf(self.library_pdf)
        for num, p in enumerate(self.pages):
            filename: str = f'{prefix}-{num+1}.pdf'
            self.progress_bar.update_text(
                f'Exportando página: {p.page_number} de {self.num_pages} | [{filename}]'
            )
            _document.add_page(p)
            _document.to_file_pdf(outdir.join_file(filename))
            _document.clear()
            
    def to_files_image(self, d: Directory, *, prefix: str = 'pdf-para-imagem'):
        """
            Exporta cada página PDF como um arquivo de imagem.
        """
        d.mkdir()
        for num, page in enumerate(self.pages):
            filename = f'{prefix}-{page.page_number}.png'
            img = self.convert_pdf_to_images.from_page_pdf(page)
            self.progress_bar.update_text(
                f'Exportando página PDF para imagem: [{num+1} de {self.num_pages}] {filename}'
            )
            img.to_file(d.join_file(filename))
            
    def to_images(self) -> List[ImageObject]:
        images_obj: List[ImageObject] = []
        for page in self.pages:
            _image: ImageObject = self.convert_pdf_to_images.from_page_pdf(page)
            images_obj.append(_image)
        return images_obj
    
    def to_document(self) -> DocumentPdf:
        return DocumentPdf(
                    self.library_pdf, progress_bar=self.progress_bar, pages=self.pages
                )
    
    def inner_images(self) -> List[ImageObject]:
        inner_images: List[ImageObject] = []
        for num, p in enumerate(self.pages):
            self.progress_bar.update(
                ((num+1)/self.num_pages) * 100,
                f'Convertendo página [{num+1} de {self.num_pages}]'
            )
            imgs: List[ImageObject] = self.convert_pdf_to_images.inner_images(p.to_bytes())
            inner_images.extend(imgs)
        return inner_images
    
    def inner_images_to_files(self, d: Directory, prefix: str = 'página-para-imagens') -> None:
        """
            Salva todas as imagens presentes nas páginas PDF, em arquivos de imagem.
        """
        d.mkdir()
        for num, page in enumerate(self.pages):
            images = self.convert_pdf_to_images.inner_images(page.to_bytes())
            if len(images) < 1:
                continue
            for n, img in enumerate(images):
                filename = f'{prefix}-{page.page_number}-img-{n+1}.png' 
                img.to_file(d.join_file(filename))
    
    def set_paisagem(self):
        for page in self.pages:
            page.set_paisagem()


#==================================================================#
# Imagens
#==================================================================#

class ImageStream(object):
    def __init__(
                self, *,
                library_image: LibraryImage = LibraryImage.OPENCV,
                library_pdf: LibraryPDF = LibraryPDF.PILPDF,
                progress_bar: ProgressBarAdapter = ProgressBarAdapter(ProgressBarSimple()),
            ):
        self.__images: List[ImageObject] = []
        self.num_images: int = len(self.__images)
        #self.progress_bar: ProgressBarAdapter = progress_bar
        self.library_image: LibraryImage = library_image
        self.library_pdf: LibraryPDF = library_pdf

        # Objeto para converter IMAGEM em pdf.
        if library_pdf == LibraryPDF.FITZ:
            self.convert_image_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_fitz(library_image)
        elif library_pdf == LibraryPDF.CANVAS:
            self.convert_image_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_canvas(library_image)
        elif library_pdf == LibraryPDF.PILPDF:
            self.convert_image_to_pdf: ImageConvertPdf = ImageConvertPdf.create_from_pil(library_image)
        else:
            raise ValueError(f'PYPDF não pode converter imagens em PDF!!')
            
        # Objeto para converter PDF em imagem
        self.convert_pdf_to_images: ConvertPdfToImage = ConvertPdfToImage(
                library_pdf=LibraryPDF.FITZ,
                library_image=library_image,
                dpi=150,
                progress_bar=progress_bar,
            )

    @property
    def progress_bar(self) -> ProgressBarAdapter:
        return self.convert_pdf_to_images.pbar
        
    @property
    def images(self) -> List[ImageObject]:
        return self.__images
    
    @images.setter
    def images(self, imgs: List[ImageObject]) -> None:
        if not isinstance(imgs, list):
            print(f'Erro: Use: list() não {type(imgs)}')
            return
        self.num_images = 0
        for img in imgs:
            self.add_image(img)
        
    def add_image(self, img: ImageObject) -> None:
        if not isinstance(img, ImageObject):
            return
        self.__images.append(img)
        self.num_images += 1
        
    def add_images(self, images: List[ImageObject]):
        maxnum: int = len(images)
        self.progress_bar.start()
        for num, i in enumerate(images):
            self.progress_bar.update(
                ((num+1)/maxnum) * 100,
                f'Adicionando imagens: [{num+1} de {maxnum}]'
            )
            self.add_image(i)
        self.progress_bar.stop()
    
    def add_file_image(self, f: File):
        img = ImageObject.create_from_file(f, library=self.library_image)
        self.add_image(img)
        
    def add_files_image(self, files: List[File]):
        maxnum: int = len(files)
        for num, f in enumerate(files):
            p = ((num + 1) / maxnum) * 100
            #print(p)
            self.progress_bar.update(
                p,
                f'Adicionando arquivos: [{num + 1} de {maxnum}]'
            )
            self.add_file_image(f)
            
    def is_null(self) -> bool:
        if self.num_images < 1:
            return True
        return False
        
    def clear(self):
        self.__images.clear()
        self.num_images = 0
        
    def to_files_image(self, d: Directory, prefix: str = 'imagem'):
        d.mkdir()
        self.progress_bar.start()
        for num, image in enumerate(self.images):
            filename = f'{prefix}-{num+1}.png'
            self.progress_bar.update(
                ((num+1)/self.num_images) * 100,
                f'Exportando imagem: {num+1} de {self.num_images} [{filename}]'
            )
            image.to_file(d.join_file(filename))
        self.progress_bar.stop()
                
    def to_pages_pdf(self) -> List[PageDocumentPdf]:
        if self.is_null():
            print(f'{__class__.__name__} Adicione imagens para prosseguir!')
            return []
        new_pages = []
        maxnum: int = len(self.images)
        self.progress_bar.start()
        for num, image in enumerate(self.images):
            self.progress_bar.update(
                ((num + 1) / maxnum) * 100,
                f'Adicionando imagens: [{num + 1} de {maxnum}]'
            )
            new_pages.append(self.convert_image_to_pdf.from_image(image))
        self.progress_bar.stop()
        return new_pages
    
    def set_paisagem(self):
        for num, img in enumerate(self.images):
            self.images[num].set_paisagem()
            
    def set_gaussian_blur(self):
        for num, img in enumerate(self.images):
            print(f'Removendo ruido de imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_gaussian()
            
    def set_backgroud_black(self):
        for num, img in enumerate(self.images):
            print(f'Escurecendo imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_background_black()
            
    def set_background_gray(self):
        for num, img in enumerate(self.images):
            print(f'Escurecendo imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_background_gray()
    
    def set_optimize(self):
        for num, img in enumerate(self.images):
            print(f'Otimizando imagem: [{num+1} de {self.num_images}]')
            self.images[num].set_optimize()
    

def get_data_from_pdfs(*, files_pdf: List[File]) -> pandas.DataFrame:
    """
        Recebe uma lista de arquivos PDF e retorna um DataFrame com os dados das cartas.
    """
    if not isinstance(files_pdf, list):
        raise ValueError(f'Erro: Use: list() não {type(files_pdf)}')
    
    data: List[pandas.DataFrame] = []
    values: List[str] = []
    doc = DocumentPdf()
    for file in files_pdf:
        doc.add_file_pdf(file)
        for page in doc.pages:
            text =  page.to_string()
            if (text is not None) and (text != ''):
                values.extend(text.split('\n'))
                data.append(
                    pandas.DataFrame(
                        {
                            'TEXT': values,
                            'ARQUIVO': [file.absolute()] * len(values)
                        }
                    )
                )

        values.clear()
        doc.clear()
    if len(data) < 1:
        return pandas.DataFrame()
    return pandas.concat(data).astype('str')
    