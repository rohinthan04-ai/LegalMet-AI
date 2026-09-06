import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

import Inspection from "./Inspection";
import InspectionHistory from "./InspectionHistory";
import Reports from "./Reports";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [currentInspection, setCurrentInspection] = useState(null);

  const [currentPage, setCurrentPage] = useState("dashboard");

  const [message, setMessage] = useState("");

  const [inspections, setInspections] = useState([]);

  // =========================
  // LOGIN
  // =========================

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/auth/login",
        {
          email: email,
          password: password,
        }
      );

      localStorage.setItem(
        "access_token",
        response.data.access_token
      );

      localStorage.setItem(
        "inspector_id",
        response.data.inspector_id
      );

      localStorage.setItem(
        "inspector_name",
        response.data.name
      );

      setLoggedIn(true);
      setMessage("");
      setCurrentPage("dashboard");

    } catch (error) {
      console.error("Login error:", error);

      if (error.response) {
        setMessage(
          error.response.data.detail ||
          "Login failed."
        );
      } else {
        setMessage(
          "Could not connect to backend."
        );
      }
    }
  };

  // =========================
  // LOAD INSPECTIONS
  // =========================

  const loadInspections = async () => {
    try {
      const token =
        localStorage.getItem("access_token");

      const response = await axios.get(
        "http://127.0.0.1:8000/inspections/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(
        "Inspections:",
        response.data
      );

      setInspections(response.data);

    } catch (error) {
      console.error(
        "Failed to load inspections:",
        error
      );
    }
  };

  // =========================
  // START NEW INSPECTION
  // =========================

  const handleStartInspection = async () => {
    try {
      const token =
        localStorage.getItem("access_token");

      const response = await axios.post(
        "http://127.0.0.1:8000/inspections/",
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(
        "New inspection:",
        response.data
      );

      setCurrentInspection(
        response.data.id
      );

      loadInspections();

    } catch (error) {
      console.error(
        "Inspection creation error:",
        error
      );

      if (error.response) {
        alert(
          error.response.data.detail ||
          "Failed to create inspection."
        );
      } else {
        alert(
          "Could not connect to backend."
        );
      }
    }
  };

  // =========================
  // OPEN EXISTING INSPECTION
  // =========================

  const handleOpenInspection = (inspectionId) => {
    setCurrentInspection(inspectionId);
  };

  // =========================
  // OPEN INSPECTION HISTORY
  // =========================

  const handleOpenHistory = () => {
    loadInspections();
    setCurrentPage("history");
  };

  // =========================
  // OPEN REPORTS
  // =========================

  const handleOpenReports = () => {
    loadInspections();
    setCurrentPage("reports");
  };

  // =========================
  // BACK TO DASHBOARD
  // =========================

  const handleBackToDashboard = () => {
    setCurrentPage("dashboard");
    loadInspections();
  };

  // =========================
  // LOGOUT
  // =========================

  const handleLogout = () => {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "inspector_id"
    );

    localStorage.removeItem(
      "inspector_name"
    );

    setLoggedIn(false);
    setCurrentInspection(null);
    setCurrentPage("dashboard");
    setInspections([]);
  };

  // =========================
  // LOAD DATA WHEN LOGGED IN
  // =========================

  useEffect(() => {
    if (loggedIn) {
      loadInspections();
    }
  }, [loggedIn]);

  // =========================
  // INSPECTION PAGE
  // =========================

  if (loggedIn && currentInspection) {
    return (
      <Inspection
        inspectionId={currentInspection}
        onBack={() => {
          setCurrentInspection(null);
          setCurrentPage("dashboard");
          loadInspections();
        }}
      />
    );
  }

  // =========================
  // INSPECTION HISTORY
  // =========================

  if (
    loggedIn &&
    currentPage === "history"
  ) {
    return (
      <InspectionHistory
        inspections={inspections}
        onOpenInspection={
          handleOpenInspection
        }
        onBack={
          handleBackToDashboard
        }
      />
    );
  }

  // =========================
  // REPORTS
  // =========================

  if (
    loggedIn &&
    currentPage === "reports"
  ) {
    return (
      <Reports
        inspections={inspections}
        onOpenInspection={
          handleOpenInspection
        }
        onOpenHistory={
          handleOpenHistory
        }
        onBack={
          handleBackToDashboard
        }
      />
    );
  }

  // =========================
  // DASHBOARD
  // =========================

  if (loggedIn) {
    const inspectorName =
      localStorage.getItem(
        "inspector_name"
      );

    const pendingCount =
      inspections.filter(
        (inspection) =>
          inspection.status !==
          "COMPLETED"
      ).length;

    const completedCount =
      inspections.filter(
        (inspection) =>
          inspection.status ===
          "COMPLETED"
      ).length;

    return (
      <div className="app">

        {/* SIDEBAR */}

        <aside className="sidebar">

          <div className="logo">
            Legal Metrology
          </div>

          {/* DASHBOARD */}

          <div
            className="nav-item active"
            onClick={() =>
              setCurrentPage("dashboard")
            }
            style={{
              cursor: "pointer",
            }}
          >
            Dashboard
          </div>

          {/* INSPECTIONS */}

          <div
            className="nav-item"
            onClick={
              handleOpenHistory
            }
            style={{
              cursor: "pointer",
            }}
          >
            Inspections
          </div>

          {/* REPORTS */}

          <div
            className="nav-item"
            onClick={
              handleOpenReports
            }
            style={{
              cursor: "pointer",
            }}
          >
            Reports
          </div>

          {/* LOGOUT */}

          <button
            className="logout"
            onClick={handleLogout}
          >
            Logout
          </button>

        </aside>

        {/* MAIN CONTENT */}

        <main className="main">

          {/* HEADER */}

          <div className="header">

            <div>

              <h1>
                Inspector Dashboard
              </h1>

              <div className="welcome">
                Welcome, {inspectorName}
              </div>

            </div>

          </div>

          {/* STATISTICS */}

          <div className="cards">

            {/* TOTAL */}

            <div className="card">

              <div className="card-title">
                Total Inspections
              </div>

              <div className="card-number">
                {
                  inspections.length
                }
              </div>

            </div>

            {/* PENDING */}

            <div className="card">

              <div className="card-title">
                Pending
              </div>

              <div className="card-number">
                {pendingCount}
              </div>

            </div>

            {/* COMPLETED */}

            <div className="card">

              <div className="card-title">
                Completed
              </div>

              <div className="card-number">
                {completedCount}
              </div>

            </div>

          </div>

          {/* START INSPECTION */}

          <div className="action-card">

            <h2>
              Start a New Inspection
            </h2>

            <p>
              Begin a new packaged commodity
              compliance inspection.
            </p>

            <button
              className="primary-button"
              onClick={
                handleStartInspection
              }
            >
              + Start New Inspection
            </button>

          </div>

          {/* RECENT INSPECTIONS */}

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
                Recent Inspections
              </h2>

              <button
                className="primary-button"
                onClick={
                  handleOpenHistory
                }
              >
                View All
              </button>

            </div>

            {inspections.length === 0 ? (

              <div className="inspection-row">

                <span>
                  No inspections found
                </span>

              </div>

            ) : (

              inspections
                .slice()
                .sort(
                  (a, b) =>
                    b.id - a.id
                )
                .slice(0, 5)
                .map(
                  (inspection) => (

                    <div
                      className="inspection-row"
                      key={
                        inspection.id
                      }
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "1fr 1fr auto",
                        gap: "20px",
                        alignItems:
                          "center",
                      }}
                    >

                      <span>
                        Inspection #
                        {
                          inspection.id
                        }
                      </span>

                      <span className="status">
                        {
                          inspection.status ||
                          "CREATED"
                        }
                      </span>

                      <button
                        className="primary-button"
                        onClick={() =>
                          handleOpenInspection(
                            inspection.id
                          )
                        }
                      >
                        Open
                      </button>

                    </div>

                  )
                )

            )}

          </div>

        </main>

      </div>
    );
  }

  // =========================
  // LOGIN PAGE
  // =========================

  return (
    <div className="login-container">

      <div className="login-card">

        <h1>
          Legal Metrology
        </h1>

        <p>
          Inspector Login
        </p>

        <form
          onSubmit={handleLogin}
        >

          <label>
            Email
          </label>

          <input
            className="login-input"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />

          <br />
          <br />

          <label>
            Password
          </label>

          <input
            className="login-input"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          <br />
          <br />

          <button
            className="login-button"
            type="submit"
          >
            Login
          </button>

        </form>

        {message && (
          <div className="error">
            {message}
          </div>
        )}

      </div>

    </div>
  );
}

export default App;