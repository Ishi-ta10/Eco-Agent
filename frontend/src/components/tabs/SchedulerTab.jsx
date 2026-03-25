import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import {
  Clock,
  Mail,
  Send,
  Play,
  Square,
  Upload,
  RefreshCw,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { schedulerAPI } from "../../api/endpoints";
import { DataTable } from "../common/DataTable";

export const SchedulerTab = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [config, setConfig] = useState(null);
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState("success");

  const { register, handleSubmit, watch, setValue } = useForm({
    defaultValues: {
      to: "",
      cc: "",
      send_time: "10:00",
      subject: "Daily Energy Report",
      custom_message: "",
    },
  });

  useEffect(() => {
    loadConfig();
    loadStatus();
    loadHistory();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await schedulerAPI.getConfig();
      setConfig(response.data);
      Object.keys(response.data).forEach((key) => {
        if (key !== "include_sections") {
          setValue(key, response.data[key]);
        }
      });
    } catch (error) {
      console.error("Failed to load config:", error);
    }
  };

  const loadStatus = async () => {
    try {
      const response = await schedulerAPI.getStatus();
      setStatus(response.data);
    } catch (error) {
      console.error("Failed to load status:", error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await schedulerAPI.getHistory(10);
      setHistory(response.data);
    } catch (error) {
      console.error("Failed to load history:", error);
    }
  };

  const handleShowMessage = (msg, type = "success", duration = 3000) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => setMessage(null), duration);
  };

  const onSubmitConfig = async (data) => {
    try {
      setIsLoading(true);
      await schedulerAPI.updateConfig(data);
      handleShowMessage("Configuration saved successfully!", "success");
      loadConfig();
    } catch (error) {
      handleShowMessage(
        "Failed to save configuration: " + error.message,
        "error",
        5000,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendNow = async () => {
    try {
      setIsLoading(true);
      await schedulerAPI.sendNow();
      handleShowMessage("Email sent successfully!", "success");
      loadHistory();
      loadStatus();
    } catch (error) {
      handleShowMessage(
        "Failed to send email: " + error.message,
        "error",
        5000,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleStart = async () => {
    try {
      setIsLoading(true);
      const sendTime = watch("send_time");
      await schedulerAPI.start(sendTime);
      handleShowMessage("Scheduler started successfully!", "success");
      loadStatus();
    } catch (error) {
      handleShowMessage(
        "Failed to start scheduler: " + error.message,
        "error",
        5000,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    try {
      setIsLoading(true);
      await schedulerAPI.stop();
      handleShowMessage("Scheduler stopped successfully!", "success");
      loadStatus();
    } catch (error) {
      handleShowMessage(
        "Failed to stop scheduler: " + error.message,
        "error",
        5000,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    if (e.target.files.length === 0) return;

    try {
      setIsLoading(true);
      const file = e.target.files[0];
      await schedulerAPI.uploadTemplate(file);
      handleShowMessage("Template uploaded successfully!", "success");
      e.target.value = "";
    } catch (error) {
      handleShowMessage(
        "Failed to upload template: " + error.message,
        "error",
        5000,
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Message Alert */}
      {message && (
        <div
          className={`rounded-2xl p-4 flex items-start gap-3 border ${
            messageType === "success"
              ? "bg-[#edf5f2] border-[#c0d8d0]"
              : "bg-[#f8eff1] border-[#debec4]"
          }`}
        >
          {messageType === "success" ? (
            <CheckCircle
              className="text-[#346f5a] mt-0.5 flex-shrink-0"
              size={20}
            />
          ) : (
            <AlertCircle
              className="text-[#924857] mt-0.5 flex-shrink-0"
              size={20}
            />
          )}
          <p
            className={
              messageType === "success"
                ? "text-[#346f5a] text-sm"
                : "text-[#924857] text-sm"
            }
          >
            {message}
          </p>
        </div>
      )}

      {/* Scheduler Status Cards */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4 flex items-center gap-2">
          <Clock className="text-[var(--accent-500)]" size={28} />
          Scheduler Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="surface-card rounded-2xl p-6">
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide mb-2">
              Status
            </p>
            <div className="flex items-center gap-3 mt-3">
              <div
                className={`w-3 h-3 rounded-full ${status?.status === "running" ? "bg-green-500 animate-pulse" : "bg-gray-500"}`}
              ></div>
              <p
                className={`text-3xl font-bold ${status?.status === "running" ? "text-[#346f5a]" : "text-[var(--text-muted)]"}`}
              >
                {status?.status === "running" ? "Running" : "Stopped"}
              </p>
            </div>
          </div>

          <div className="surface-card rounded-2xl p-6">
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide mb-2">
              Next Run
            </p>
            <p className="text-lg font-semibold text-[var(--text-primary)] mt-3">
              {status?.next_run
                ? new Date(status.next_run).toLocaleString("en-IN")
                : "Not scheduled"}
            </p>
          </div>

          <div className="surface-card rounded-2xl p-6">
            <p className="text-[var(--text-muted)] text-sm uppercase tracking-wide mb-2">
              Last Run
            </p>
            <p className="text-lg font-semibold text-[var(--text-primary)] mt-3">
              {status?.last_run?.timestamp
                ? new Date(status.last_run.timestamp).toLocaleString("en-IN")
                : "Never"}
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <form
        onSubmit={handleSubmit(onSubmitConfig)}
        className="surface-card rounded-2xl p-8"
      >
        <h2 className="text-2xl font-bold section-title mb-6">
          Email Configuration
        </h2>

        <div className="space-y-4">
          <div>
            <label className="field-label block text-sm font-semibold uppercase tracking-wide mb-2">
              To (Recipients)
            </label>
            <input
              type="text"
              placeholder="email1@example.com, email2@example.com"
              {...register("to")}
              className="field-input"
            />
          </div>

          <div>
            <label className="field-label block text-sm font-semibold uppercase tracking-wide mb-2">
              CC (Optional)
            </label>
            <input
              type="text"
              placeholder="cc@example.com"
              {...register("cc")}
              className="field-input"
            />
          </div>

          <div>
            <label className="field-label block text-sm font-semibold uppercase tracking-wide mb-2">
              Send Time
            </label>
            <input
              type="time"
              {...register("send_time")}
              className="field-input"
            />
          </div>

          <div>
            <label className="field-label block text-sm font-semibold uppercase tracking-wide mb-2">
              Subject
            </label>
            <input
              type="text"
              placeholder="Email subject"
              {...register("subject")}
              className="field-input"
            />
          </div>

          <div>
            <label className="field-label block text-sm font-semibold uppercase tracking-wide mb-2">
              Custom Message
            </label>
            <textarea
              placeholder="Optional custom message to include in email"
              {...register("custom_message")}
              rows="4"
              className="field-input resize-none"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary disabled:bg-gray-400"
          >
            <Mail size={16} />
            {isLoading ? "Saving..." : "Save Configuration"}
          </button>
        </div>
      </form>

      {/* Template Upload */}
      <div className="surface-card rounded-2xl p-8">
        <h2 className="text-2xl font-bold section-title mb-4">
          Custom Excel Template
        </h2>
        <div className="flex items-center gap-4 flex-wrap">
          <label className="btn-success cursor-pointer">
            <Upload size={16} />
            Upload Template
            <input
              type="file"
              accept=".xlsx"
              onChange={handleFileUpload}
              disabled={isLoading}
              className="hidden"
            />
          </label>
          <p className="text-sm text-[var(--text-muted)]">
            Upload a custom Excel template for email attachments
          </p>
        </div>
      </div>

      {/* Scheduler Controls */}
      <div className="surface-card rounded-2xl p-8">
        <h2 className="text-2xl font-bold section-title mb-6">Controls</h2>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={handleStart}
            disabled={isLoading || status?.status === "running"}
            className="btn-success disabled:bg-gray-400 disabled:shadow-none"
          >
            <Play size={16} />
            Start Scheduler
          </button>

          <button
            onClick={handleStop}
            disabled={isLoading || status?.status === "stopped"}
            className="btn-danger disabled:bg-gray-400 disabled:shadow-none"
          >
            <Square size={16} />
            Stop Scheduler
          </button>

          <button
            onClick={handleSendNow}
            disabled={isLoading}
            className="btn-primary disabled:bg-gray-400 disabled:shadow-none"
          >
            <Send size={16} />
            Send Now (Test)
          </button>

          <button
            onClick={() => {
              loadStatus();
              loadHistory();
            }}
            disabled={isLoading}
            className="btn-neutral disabled:bg-gray-400"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Send History */}
      <div>
        <h2 className="text-2xl font-bold section-title mb-4">Send History</h2>
        {history.length > 0 ? (
          <DataTable data={history} hideColumns={[]} />
        ) : (
          <div className="surface-card rounded-2xl p-12 text-center">
            <p className="text-[var(--text-muted)] text-lg">
              No send history yet
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
