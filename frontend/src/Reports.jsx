import { useEffect, useState } from "react";
import axios from "axios";

function Reports({
  inspections,
  onBack,
  onOpenInspection,
}) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  // =========================
  // LOAD REPORTS
  // =========================

  const loadReports = async () => {
    try {
      setLoading(true);

      const token =
        localStorage.getItem("access_token");

      const generatedReports = [];

      // Check each inspection for a report
      for (const inspection of inspections) {
        try {
          const response = await axios.get(
            `http://127.0.0.1:8000/inspections/${inspection.id}/report`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          generatedReports.push({
            inspection: inspection,
            report: response.data,
          });

        } catch (error) {
          // 404 simply means report hasn't
          // been generated yet
          if (
            error.response?.status !== 404
          ) {
            console.error(
              `Failed to load report for inspection ${inspection.id}:`,
              error
            );
          }
        }
      }

      setReports(generatedReports);

    } catch (error) {
      console.error(
        "Failed to load reports:",
        error
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOAD ON PAGE OPEN
  // =========================

  useEffect(() => {
    loadReports();
  }, [inspections]);

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
  // DOWNLOAD PDF
  // =========================

  const handleDownloadPdf = async (
    inspectionId
  ) => {
    try {
      const token =
        localStorage.getItem("access_token");

      const response = await axios.get(
        `http://127.0.0.1:8000/inspections/${inspectionId}/report/pdf`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: "blob",
        }
      );

      const blob = new Blob(
        [response.data],
        {
          type: "application/pdf",
        }
      );

      const url =
        window.URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        `inspection_report_${inspectionId}.pdf`;

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error(
        "PDF download failed:",
        error
      );

      alert(
        "Failed to download the report."
      );
    }
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

        <div
          className="nav-item"
          onClick={() =>
            onBack("history")
          }
          style={{ cursor: "pointer" }}
        >
          Inspections
        </div>

        <div className="nav-item active">
          Reports
        </div>

      </aside>

      {/* MAIN */}

      <main className="main">

        {/* HEADER */}

        <div className="header">

          <div>

            <h1>
              Reports
            </h1>

            <div className="welcome">
              Generated inspection reports
            </div>

          </div>

          <button
            className="primary-button"
            onClick={onBack}
          >
            ← Dashboard
          </button>

        </div>

        {/* REPORT LIST */}

        <div className="recent">

          <div
            style={{
              display: "flex",
              justifyContent:
                "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >

            <h2>
              Inspection Reports
            </h2>

            <button
              className="primary-button"
              onClick={loadReports}
              disabled={loading}
            >
              {loading
                ? "Refreshing..."
                : "↻ Refresh"}
            </button>

          </div>

          {/* LOADING */}

          {loading && (
            <div className="inspection-row">
              Loading reports...
            </div>
          )}

          {/* NO REPORTS */}

          {!loading &&
            reports.length === 0 && (
              <div className="inspection-row">
                <span>
                  No reports have been
                  generated yet.
                </span>
              </div>
            )}

          {/* REPORTS */}

          {!loading &&
            reports
              .slice()
              .sort(
                (a, b) =>
                  b.inspection.id -
                  a.inspection.id
              )
              .map(
                ({
                  inspection,
                  report,
                }) => (

                  <div
                    className="inspection-row"
                    key={report.id}
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "1.2fr 1.5fr 1fr auto auto",
                      gap: "15px",
                      alignItems:
                        "center",
                    }}
                  >

                    {/* INSPECTION */}

                    <span>
                      <strong>
                        Inspection #
                        {inspection.id}
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
                      COMPLETED
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
                      View
                    </button>

                    {/* DOWNLOAD */}

                    <button
                      className="primary-button"
                      onClick={() =>
                        handleDownloadPdf(
                          inspection.id
                        )
                      }
                    >
                      Download PDF
                    </button>

                  </div>

                )
              )}

        </div>

      </main>

    </div>
  );
}

export default Reports;