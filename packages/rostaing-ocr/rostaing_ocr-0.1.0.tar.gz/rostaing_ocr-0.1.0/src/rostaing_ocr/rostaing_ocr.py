import os
import fitz  # PyMuPDF
import pytesseract
from markitdown import MarkItDown
import io
from PIL import Image
# N.B. : 'ImageOps' n'était pas utilisé, je l'ai retiré pour plus de propreté.
from typing import List, Union, Optional, Dict, Tuple # Tuple n'est plus nécessaire mais bonne pratique à connaître

class RostaingOCR:
    """
    Une classe pour convertir, extraire et sauvegarder le texte de fichiers
    (images, PDF scannés) aux formats .txt et .md. La reconnaissance est
    optimisée par un prétraitement des images.
    
    Utilisation :
        # Comportement par défaut (sauvegarde uniquement)
        extractor = RostaingOCR("fichier.pdf", output_basename="resultat")
        
        # Sauvegarde ET affichage dans la console
        extractor = RostaingOCR("fichier.pdf", output_basename="resultat", print_to_console=True)
    """

    def __init__(self,
                 input_path_or_paths: Union[str, List[str]],
                 output_basename: str = "output",
                 print_to_console: bool = False,
                 languages: List[str] = ['fra', 'eng'],
                 tesseract_cmd: Optional[str] = None):
        """
        Initialise ET lance le processus d'extraction complet.

        Args:
            input_path_or_paths (Union[str, List[str]]):
                Chemin vers un fichier source unique ou une liste de chemins.
            output_basename (str):
                Nom de base pour les fichiers de sortie (sans extension).
                Générera '{output_basename}.txt' et '{output_basename}.md'.
            print_to_console (bool):
                Si True, le contenu Markdown extrait sera affiché dans la console.
            languages (List[str]): 
                Liste des langues à utiliser pour l'OCR.
            tesseract_cmd (Optional[str]): 
                Chemin vers l'exécutable Tesseract.
        """
        # --- 1. Configuration ---
        if isinstance(input_path_or_paths, str):
            self.input_paths = [input_path_or_paths]
        else:
            self.input_paths = input_path_or_paths

        self.output_basename = output_basename
        self.output_txt_path = f"{output_basename}.txt"
        self.output_md_path = f"{output_basename}.md"

        self.print_to_console = print_to_console
        self.tesseract_lang_string = '+'.join(languages)
        self.md_converter = MarkItDown()
        self.results: Dict[str, Optional[str]] = {}

        for path in self.input_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The specified input file does not exist: {path}")

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        print(f"RostaingOCR initialized. Starting processing...")
        print(f"Output files: '{self.output_txt_path}' and '{self.output_md_path}'")
        if self.print_to_console:
            print("Console display: Enabled")

        # --- 2. Exécution immédiate du traitement ---
        self._run_extraction_workflow()
        
        print("\nProcessing complete.")

    def _run_extraction_workflow(self):
        """(Privé) Gère le flux de travail pour tous les fichiers."""
        all_final_content = []
        
        for i, file_path in enumerate(self.input_paths):
            print(f"\n--- Processing {os.path.basename(file_path)} ({i+1}/{len(self.input_paths)}) ---")
            
            # CORRIGÉ: La méthode retourne maintenant une seule chaîne (le contenu Markdown)
            extracted_content = self._extract_text_from_single_file(file_path)
            
            self.results[file_path] = extracted_content
            
            if extracted_content:
                # Ajoute un titre pour la consolidation si plusieurs fichiers sont traités
                content_with_header = f"# Content from : {os.path.basename(file_path)}\n\n{extracted_content}"
                all_final_content.append(content_with_header)
                print(f"--- SUCCESS for '{os.path.basename(file_path)}' ---")

                # Affichage console immédiat pour ce fichier
                if self.print_to_console:
                    print("\n" + "="*20 + f" CONTENT OF {os.path.basename(file_path)} " + "="*20)
                    print(extracted_content)
                    print("="* (42 + len(os.path.basename(file_path))) + "\n")
            else:
                print(f"--- FAILED for '{os.path.basename(file_path)}' ---")

        if all_final_content:
            # Consolide le contenu de tous les fichiers traités
            final_output_string = "\n\n---\n\n".join(all_final_content)
            self._save_outputs(final_output_string)

    # CORRIGÉ: La signature de la fonction retourne maintenant un simple Optional[str]
    def _extract_text_from_single_file(self, input_path: str) -> Optional[str]:
        """(Privé) Orchestre le processus pour un seul fichier et retourne le contenu Markdown."""
        searchable_pdf_path = self._convert_to_searchable_pdf(input_path)
        
        if not searchable_pdf_path:
            return None

        extracted_content = None
        try:
            print(f"\n[Step 2/3] Extracting text and converting to Markdown...")
            result = self.md_converter.convert(searchable_pdf_path)
            
            # CORRIGÉ: Utilisation de .text_content qui contient bien le Markdown
            extracted_content = result.text_content
            
            print("  - Extraction and conversion successful.")
            
        except Exception as e:
            # Erreur plus spécifique et utile pour le débogage
            print(f"  - ERROR during extraction with MarkItDown : {e}")
        finally:
            print("[Cleanup] Deleting temporary file...")
            if searchable_pdf_path and os.path.exists(searchable_pdf_path):
                os.remove(searchable_pdf_path)
                print(f"  - '{searchable_pdf_path}' supprimé.")
        
        return extracted_content

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """(Privé) Prétraite une image pour optimiser l'OCR."""
        # Conversion en niveaux de gris pour améliorer le contraste
        return image.convert('L')

    def _convert_to_searchable_pdf(self, input_path: str) -> Optional[str]:
        """(Privé) Convertit un fichier en PDF cherchable temporaire avec prétraitement d'image."""
        print(f"[Step 1/3] Converting to searchable PDF...")
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        temp_output_path = f"{base_name}_temp_searchable.pdf"
        output_pdf = fitz.open()
        
        # Utilisation de 'with' pour garantir la fermeture des ressources
        try:
            with fitz.open(input_path) as input_doc:
                for i, page in enumerate(input_doc):
                    print(f"  - Processing page {i+1}/{len(input_doc)}...")
                    pix = page.get_pixmap(dpi=300)
                    img_bytes = pix.tobytes("png")
                    
                    img = Image.open(io.BytesIO(img_bytes))
                    preprocessed_img = self._preprocess_image(img)
                    
                    result = pytesseract.image_to_pdf_or_hocr(preprocessed_img, lang=self.tesseract_lang_string, extension='pdf')
                    
                    with fitz.open("pdf", result) as ocr_pdf:
                        new_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)
                        new_page.insert_image(page.rect, stream=img_bytes) 
                        new_page.show_pdf_page(new_page.rect, ocr_pdf, 0)

        except Exception:
            print(f"  - Warning: fitz could not open '{input_path}' directly. Attempting with Pillow...")
            try:
                with Image.open(input_path) as img:
                    preprocessed_img = self._preprocess_image(img.convert("RGB")) # Convertir en RGB avant pour la compatibilité
                    
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(preprocessed_img, lang=self.tesseract_lang_string, extension='pdf')
                    
                    with fitz.open("pdf", pdf_bytes) as ocr_pdf:
                        # Reconstruire un PDF avec l'image visuelle
                        img_as_bytes = io.BytesIO()
                        img.save(img_as_bytes, format='PNG')
                        img_as_bytes.seek(0)

                        page = output_pdf.new_page(width=img.width, height=img.height)
                        page.insert_image(page.rect, stream=img_as_bytes.read())
                        page.show_pdf_page(page.rect, ocr_pdf, 0)

            except Exception as e2:
                print(f"  - FATAL ERROR: Could not process file '{input_path}'. EError : {e2}")
                output_pdf.close()
                return None
        
        if len(output_pdf) > 0:
            output_pdf.save(temp_output_path, garbage=4, deflate=True, clean=True)
            print(f"  - Temporary searchable PDF created : '{temp_output_path}'")
        else:
            print("  - ERROR: No pages were generated.")
            temp_output_path = None
        
        output_pdf.close()
        return temp_output_path

    def _save_outputs(self, final_content: str):
        """(Privé) Sauvegarde le contenu Markdown consolidé dans les fichiers .txt et .md."""
        print(f"\n[Step 3/3] Saving consolidated content...")
        
        for path in [self.output_md_path, self.output_txt_path]:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                print(f"  - Successfully saved to '{path}'.")
            except IOError as e:
                print(f"  - ERROR: Could not write to file '{path}'. Error : {e}")

    def __str__(self) -> str:
        """Représentation textuelle de l'objet pour afficher un résumé des résultats."""
        summary_lines = [f"--- RostaingOCR Extraction Summary ---"]
        summary_lines.append(f"Generated output files: '{self.output_txt_path}' et '{self.output_md_path}'")
        
        for file_path, text_content in self.results.items():
            status = "✅ Success" if text_content else "❌ Failure"
            line = f"\n  - Processed file : {os.path.basename(file_path)}\n"
            line += f"    Status         : {status}"
            summary_lines.append(line)
        return "\n".join(summary_lines)