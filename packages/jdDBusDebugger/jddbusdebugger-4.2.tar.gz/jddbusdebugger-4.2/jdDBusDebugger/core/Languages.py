from PyQt6.QtCore import QCoreApplication


def get_language_names() -> dict[str, str]:
    return {
        "en": QCoreApplication.translate("Language", "English"),
        "de": QCoreApplication.translate("Language", "German"),
        "nl": QCoreApplication.translate("Language", "Dutch"),
        "ar": QCoreApplication.translate("Language", "Arabic"),
        "pt_BR": QCoreApplication.translate("Language", "Portuguese (Brazil)"),
    }
