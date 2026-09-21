import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      "dashboard.title": "NAVAM Command Center",
      "season.monsoon": "Monsoon",
      "season.dry": "Dry",
      "season.winter": "Winter",
      "nav.commandCenter": "Command Center",
      "nav.gisMap": "GIS Map",
      "nav.habitationDetail": "Habitation Detail",
      "nav.explainability": "Explainability",
      "nav.priorityList": "Priority List",
      "nav.safeSiteFinder": "Safe Site Finder",
      "nav.capacityPlan": "Capacity Plan",
      "nav.policyEditor": "Policy Editor (Admin)",
    }
  },
  hi: {
    translation: {
      "dashboard.title": "नवम कमांड सेंटर",
      "season.monsoon": "मानसून",
      "season.dry": "सूखा",
      "season.winter": "सर्दी",
      "nav.commandCenter": "कमांड सेंटर",
      "nav.gisMap": "जीआईएस मैप",
      "nav.habitationDetail": "बस्ती विवरण",
      "nav.explainability": "व्याख्या",
      "nav.priorityList": "प्राथमिकता सूची",
      "nav.safeSiteFinder": "सुरक्षित स्थल खोजक",
      "nav.capacityPlan": "क्षमता योजना",
      "nav.policyEditor": "नीति संपादक",
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "en",
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
