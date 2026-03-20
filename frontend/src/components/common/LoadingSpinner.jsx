import React from "react";
import { Zap } from "lucide-react";

export const LoadingSpinner = ({ size = "md", message = "Loading..." }) => {
  const sizeClasses = {
    sm: "w-6 h-6",
    md: "w-16 h-16",
    lg: "w-20 h-20",
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className={`${sizeClasses[size]} relative`}>
        <div
          className="absolute inset-0 rounded-full animate-spin"
          style={{
            background:
              "linear-gradient(120deg, var(--accent-500), var(--accent-600))",
          }}
        ></div>
        <div className="absolute inset-1 rounded-full flex items-center justify-center bg-[var(--surface)]">
          <Zap
            className="text-[var(--accent-500)]"
            size={size === "lg" ? 28 : size === "sm" ? 12 : 20}
          />
        </div>
      </div>
      {message && (
        <p className="text-[var(--text-muted)] text-base font-medium mt-4">
          {message}
        </p>
      )}
    </div>
  );
};
