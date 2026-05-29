import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Main from "./components/Main.jsx";
import QuoteModal from "./components/QuoteModal.jsx";

export default function App() {
  const [quoteOpen, setQuoteOpen] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("softara-theme") ||
      (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("softara-theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");

  return (
    <div className="layout">
      <Sidebar onOpenQuote={() => setQuoteOpen(true)} theme={theme} onToggleTheme={toggleTheme} />
      <Main onOpenQuote={() => setQuoteOpen(true)} />
      {quoteOpen && <QuoteModal onClose={() => setQuoteOpen(false)} />}
    </div>
  );
}
