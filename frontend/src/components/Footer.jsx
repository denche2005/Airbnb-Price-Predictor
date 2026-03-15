import { Github, Linkedin } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img
              src="/logo.png"
              alt="Airbnb Predictor"
              className="h-8 w-auto object-contain"
            />
            <span className="text-sm text-gray-airbnb hidden sm:inline">
              AI-Powered Pricing Accuracy
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-airbnb">
            <span>Built by Denys Cherednychenko</span>
            <a
              href="https://github.com/denche2005/Airbnb-Price-Predictor"
              target="_blank"
              rel="noreferrer"
              className="hover:text-dark transition-colors"
            >
              <Github size={18} />
            </a>
            <a
              href="https://www.linkedin.com/in/denys-cherednychenko2005/"
              target="_blank"
              rel="noreferrer"
              className="hover:text-dark transition-colors"
            >
              <Linkedin size={18} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
