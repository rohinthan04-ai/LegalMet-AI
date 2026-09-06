import { useEffect, useState } from "react";
import axios from "axios";

function InspectionHistory({ inspections, onOpenInspection, onBack }) {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState(inspections || []);

  // =========================
  // LOAD INSPECTIONS
  // =========================

  const loadHistory = async () => {
    try {
      setLoading(true);

      const token = localStorage.getItem("access_token");

      const response = await axios.get(
        "http://127.0.0.1:8000/inspections/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setHistory(response.data);
    } catch (error) {
      console.error("Failed to load inspection history:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // =========================
  // FORMAT DATE
  // =========================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "N/A";
    }

    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
      return dateString;
    }

    return date.toLocaleString();
  };

  // =========================
  // STATUS
  // =========================

  const getStatus = (inspection) => {
    return inspection.status || "CREATED";
  };

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="logo">
          Legal Metrology
        </div>

        <div
          className="nav-item"
          onClick={onBack}
          style={{ cursor: "pointer" }}
        >
          Dashboard
        </div>

        <div className="nav-item active">
          Inspections
        </div>

        <div className="nav-item">
          Reports
        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main">

        {/* HEADER */}

        <div className="header">

          <div>
            <h1>
              Inspection History
            </h1>

            <div className="welcome">
              View your previous inspections
            </div>
          </div>

          <button
            className="primary-button"
            onClick={onBack}
          >
            ← Dashboard
          </button>

        </div>

        {/* CONTENT */}

        <div className="recent">

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <h2>
              All Inspections
            </h2>

            <button
              className="primary-button"
              onClick={loadHistory}
              disabled={loading}
            >
              {loading ? "Refreshing..." : "↻ Refresh"}
            </button>
          </div>

          {/* LOADING */}

          {loading && history.length === 0 && (
            <div className="inspection-row">
              <span>
                Loading inspection history...
              </span>
            </div>
          )}

          {/* EMPTY */}

          {!loading && history.length === 0 && (
            <div className="inspection-row">
              <span>
                No inspections found.
              </span>
            </div>
          )}

          {/* INSPECTION LIST */}

          {history
            .slice()
            .sort((a, b) => b.id - a.id)
            .map((inspection) => {

              const status = getStatus(inspection);

              return (
                <div
                  className="inspection-row"
                  key={inspection.id}
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "1.2fr 1.5fr 1fr auto",
                    gap: "20px",
                    alignItems: "center",
                  }}
                >

                  {/* ID */}

                  <span>
                    <strong>
                      Inspection #{inspection.id}
                    </strong>
                  </span>

                  {/* DATE */}

                  <span>
                    {formatDate(
                      inspection.created_at
                    )}
                  </span>

                  {/* STATUS */}

                  <span className="status">
                    {status}
                  </span>

                  {/* OPEN */}

                  <button
                    className="primary-button"
                    onClick={() =>
                      onOpenInspection(
                        inspection.id
                      )
                    }
                  >
                    Open
                  </button>

                </div>
              );
            })}

        </div>

      </main>

    </div>
  );
}

export default InspectionHistory;