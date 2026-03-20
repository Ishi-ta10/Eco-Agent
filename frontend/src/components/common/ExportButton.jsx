import React from "react";
import { Download, CheckCircle } from "lucide-react";

export const ExportButton = ({
  onClick,
  isLoading = false,
  label = "Export Excel",
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className="flex items-center gap-2 px-6 py-2.5 bg-[var(--success-600)] text-white font-semibold rounded-xl hover:brightness-110 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md"
    >
      {isLoading ? (
        <>
          <div className="animate-spin">
            <Download size={16} />
          </div>
          Exporting...
        </>
      ) : (
        <>
          <Download size={16} />
          {label}
        </>
      )}
    </button>
  );
};
