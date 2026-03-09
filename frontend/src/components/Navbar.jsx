import { Link, useLocation } from "react-router-dom";
import { Home, BarChart3, Info } from "lucide-react";

const links = [
  { to: "/", label: "Home", icon: Home },
  { to: "/predict", label: "Predict", icon: BarChart3 },
  { to: "/about", label: "About", icon: Info },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-gray-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-full border border-airbnb/30 bg-airbnb/10 flex items-center justify-center">
            <span className="text-airbnb font-extrabold text-base tracking-tight">
              p
            </span>
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-[22px] font-extrabold text-dark tracking-tight">
              price<span className="text-airbnb">bnb</span>
            </span>
            <span className="text-[11px] text-gray-airbnb hidden sm:block">
              Worldwide Airbnb price predictor
            </span>
          </div>
        </Link>

        <ul className="flex items-center gap-1 bg-gray-100 rounded-full px-1 py-1">
          {links.map(({ to, label, icon: Icon }) => {
            const active = pathname === to;
            return (
              <li key={to}>
                <Link
                  to={to}
                  className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    active
                      ? "bg-white text-dark shadow-sm"
                      : "text-gray-airbnb hover:bg-white hover:text-dark"
                  }`}
                >
                  <Icon size={16} />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
