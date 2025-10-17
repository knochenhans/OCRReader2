import os

from model_trainer.line_exporter import LineExporter  # type: ignore
from model_trainer.model_trainer import ModelTrainer  # type: ignore
from model_trainer.model_trainer_dialog import ModelTrainerDialog  # type: ignore
from PySide6.QtWidgets import QMessageBox


class ModelTrainingActions:
    def __init__(self, main_window, project_manager):
        self.main_window = main_window
        self.project_manager = project_manager

    def train_model(
        self,
        model_name: str,
        base_dir: str,
        tesseract_data_path: str,
        tesseract_data_original_path: str,
    ) -> None:
        model_trainer = ModelTrainer(
            model_name,
            base_dir,
            tesseract_data_original_path,
            tesseract_data_path,
        )

        iteration_count = self.main_window.application_settings.get(
            "training_iterations", 400
        )
        new_model_path = model_trainer.train_model(
            iteration_count,
        )

        response = self.main_window.show_confirmation_dialog(
            "New Model Path Detected",
            "A finetuned model has been created. Do you want to set it as the new model path for the project?",
        )
        if response:
            if new_model_path != "":
                project = self.project_manager.current_project

                if project:
                    if project.settings:
                        project.settings.set("tesseract_data_path", new_model_path)

    def open_train_model_dialog(self) -> None:
        project = self.project_manager.current_project

        if not project:
            return

        if not project.settings:
            return

        langs = project.settings.get("langs", ["eng"])

        if not langs:
            return

        # TODO: Use first language in list for now
        lang = langs[0]

        train_data_path = os.path.join(project.folder, "training")

        os.makedirs(train_data_path, exist_ok=True)

        # Check if no box IDs are flagged for training
        if not self.main_window.box_ids_flagged_for_training:
            QMessageBox.information(
                self.main_window,
                "No Box IDs Flagged",
                "No box IDs are flagged for training. All boxes will be used from the start of the project, using confidence threshold set in the general settings.",
            )

            # Get all box IDs from the project
            for page in project.pages:
                for box in page.layout.ocr_boxes:
                    self.main_window.box_ids_flagged_for_training.append(box.id)

            print("Collected Box IDs:", self.main_window.box_ids_flagged_for_training)

        line_exporter = LineExporter(
            project,
            train_data_path,
        )

        application_settings = self.main_window.application_settings

        confidence_threshold = application_settings.get(
            "training_line_confidence_threshold", 90
        )
        max_training_lines = application_settings.get("max_training_lines", 100)
        remove_existing_training_lines = application_settings.get(
            "remove_training_lines_before_training", True
        )

        line_exporter.export_project_lines(
            confidence_threshold,
            max_training_lines,
            self.main_window.box_ids_flagged_for_training,
            remove_existing=remove_existing_training_lines,
        )

        tesseract_original_data_path = project.settings.get("tesseract_data_path", "")

        model_trainer_dialog = ModelTrainerDialog(
            self.main_window,
            lang,
            train_data_path,
            tesseract_original_data_path,
            train_data_path,
        )

        model_trainer_dialog.train_button_clicked.connect(
            lambda: self.train_model(
                lang,
                train_data_path,
                train_data_path,
                tesseract_original_data_path,
            )
        )

        model_trainer_dialog.exec()
