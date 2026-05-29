import { useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Main from "./components/Main.jsx";
import QuoteModal from "./components/QuoteModal.jsx";

export default function App() {
  const [quoteOpen, setQuoteOpen] = useState(false);

  return (
    <div className="layout">
      <Sidebar onOpenQuote={() => setQuoteOpen(true)} />
      <Main onOpenQuote={() => setQuoteOpen(true)} />
      {quoteOpen && <QuoteModal onClose={() => setQuoteOpen(false)} />}
    </div>
  );
}
