import { useState, useEffect } from "react";
import axios from "axios";

function Inspection({ inspectionId, onBack }) {
  const [image, setImage] = useState(null);
  const [imageType] = useState("product");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // =========================================================
  // INSPECTOR VERIFICATION
  // =========================================================

  const [verifiedData, setVerifiedData] = useState(null);
  const [verified, setVerified] = useState(false);

  // =========================================================
  // PRODUCT CATEGORY
  // =========================================================

  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");

  // =========================================================
  // CHECKLIST
  // =========================================================

  const [checklist, setChecklist] = useState(null);
  const [creatingChecklist, setCreatingChecklist] = useState(false);

  // =========================================================
  // EVALUATION
  // =========================================================

  const [evaluating, setEvaluating] = useState(false);
  const [evaluation, setEvaluation] = useState(null);

  // =========================================================
  // REPORT
  // =========================================================

  const [generatingReport, setGeneratingReport] = useState(false);
  const [report, setReport] = useState(null);

  // =========================================================
  // LOAD PRODUCT CATEGORIES
  // =========================================================

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const token = localStorage.getItem("access_token");

        const response = await axios.get(
          "http://127.0.0.1:8000/inspections/rule-categories",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        console.log("Product categories:", response.data);

        setCategories(response.data);
      } catch (error) {
        console.error(
          "Failed to load product categories:",
          error
        );

        setError(
          "Could not load product categories."
        );
      }
    };

    loadCategories();
  }, []);

  // =========================================================
  // IMAGE UPLOAD + GEMINI
  // =========================================================

  const handleUpload = async () => {
    if (!image) {
      setError("Please select a product image.");
      return;
    }

    setLoading(true);
    setError("");

    setResult(null);
    setVerified(false);
    setVerifiedData(null);

    setSelectedCategory("");
    setChecklist(null);
    setEvaluation(null);
    setReport(null);

    try {
      const token =
        localStorage.getItem("access_token");

      const formData = new FormData();

      formData.append("image", image);
      formData.append("image_type", imageType);

      const response = await axios.post(
        `http://127.0.0.1:8000/inspections/${inspectionId}/images`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(
        "Gemini extraction result:",
        response.data
      );

      setResult(response.data);

      setVerifiedData(
        JSON.parse(
          JSON.stringify(
            response.data.structured_data.ocr_data
          )
        )
      );
    } catch (error) {
      console.error(
        "Upload error:",
        error
      );

      if (error.response) {
        setError(
          error.response.data.detail ||
            "Image processing failed."
        );
      } else {
        setError(
          "Could not connect to backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // UPDATE PRODUCT FIELD
  // =========================================================

  const handleFieldChange = (
    field,
    value
  ) => {
    setVerifiedData((previous) => ({
      ...previous,
      [field]: value,
    }));

    setVerified(false);
    setChecklist(null);
    setEvaluation(null);
    setReport(null);
  };

  // =========================================================
  // UPDATE CONSUMER CARE
  // =========================================================

  const handleConsumerCareChange = (
    field,
    value
  ) => {
    setVerifiedData((previous) => ({
      ...previous,
      consumer_care_details: {
        ...previous.consumer_care_details,
        [field]: value,
      },
    }));

    setVerified(false);
    setChecklist(null);
    setEvaluation(null);
    setReport(null);
  };

  // =========================================================
  // VERIFY + SAVE PRODUCT DATA
  // =========================================================

  const handleVerify = async () => {
    if (!verifiedData) {
      return;
    }

    try {
      setError("");
      setLoading(true);

      const token =
        localStorage.getItem("access_token");

      await axios.post(
        `http://127.0.0.1:8000/inspections/${inspectionId}/structured-data`,
        verifiedData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log(
        "Verified product data saved successfully."
      );

      setVerified(true);
    } catch (error) {
      console.error(
        "Verification save error:",
        error
      );

      if (error.response) {
        setError(
          error.response.data.detail ||
            "Failed to save verified information."
        );
      } else {
        setError(
          "Could not connect to backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // CREATE / LOAD CHECKLIST
  // =========================================================

  const handleCreateChecklist = async () => {
    if (!selectedCategory) {
      setError(
        "Please select a product category."
      );
      return;
    }

    if (!verified) {
      setError(
        "Please verify the product information first."
      );
      return;
    }

    try {
      setError("");
      setCreatingChecklist(true);
      setEvaluation(null);
      setReport(null);

      const token =
        localStorage.getItem("access_token");

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      // -------------------------------------------------------
      // CHECK IF CHECKLIST ALREADY EXISTS
      // -------------------------------------------------------

      console.log(
        "Checking for existing checklist..."
      );

      try {
        const existingResponse =
          await axios.get(
            `http://127.0.0.1:8000/inspections/${inspectionId}/checklist`,
            {
              headers,
            }
          );

        console.log(
          "Existing checklist found:",
          existingResponse.data
        );

        const existingChecklist =
          existingResponse.data;

        const existingCategory =
          existingChecklist?.rules?.category_code;

        if (
          existingCategory &&
          existingCategory !== selectedCategory
        ) {
          setError(
            `This inspection already has a checklist for category "${existingCategory}".`
          );

          return;
        }

        setChecklist(existingChecklist);

        return;
      } catch (error) {
        if (
          error.response &&
          error.response.status !== 404
        ) {
          throw error;
        }
      }

      // -------------------------------------------------------
      // CREATE NEW CHECKLIST
      // -------------------------------------------------------

      console.log(
        "No existing checklist found."
      );

      console.log(
        "Creating checklist for:",
        selectedCategory
      );

      const response = await axios.post(
        `http://127.0.0.1:8000/inspections/${inspectionId}/checklist`,
        {
          category_code: selectedCategory,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log(
        "Checklist created:",
        response.data
      );

      setChecklist(response.data);
    } catch (error) {
      console.error(
        "Checklist creation error:",
        error
      );

      if (error.response) {
        console.log(
          "Checklist backend response:",
          error.response.data
        );

        setError(
          error.response.data.detail ||
            "Failed to create compliance checklist."
        );
      } else {
        setError(
          "Could not connect to backend."
        );
      }
    } finally {
      setCreatingChecklist(false);
    }
  };

  // =========================================================
  // EVALUATE COMPLIANCE
  // =========================================================

  const handleEvaluate = async () => {
    if (!checklist) {
      setError(
        "Please generate the compliance checklist first."
      );
      return;
    }

    if (!verified) {
      setError(
        "Please verify the product information first."
      );
      return;
    }

    try {
      setError("");
      setEvaluating(true);
      setEvaluation(null);
      setReport(null);

      const token =
        localStorage.getItem("access_token");

      console.log(
        "Starting compliance evaluation..."
      );

      const response = await axios.post(
        `http://127.0.0.1:8000/inspections/${inspectionId}/evaluation`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log(
        "Evaluation result:",
        response.data
      );

      setEvaluation(response.data);
    } catch (error) {
      console.error(
        "Evaluation error:",
        error
      );

      if (error.response) {
        setError(
          error.response.data.detail ||
            "Compliance evaluation failed."
        );
      } else {
        setError(
          "Could not connect to backend."
        );
      }
    } finally {
      setEvaluating(false);
    }
  };

  // =========================================================
  // GENERATE REPORT
  // =========================================================

  const handleGenerateReport = async () => {
    if (!evaluation) {
      setError(
        "Please complete the compliance evaluation first."
      );
      return;
    }

    try {
      setError("");
      setGeneratingReport(true);

      const token =
        localStorage.getItem("access_token");

      console.log(
        "Generating inspection report..."
      );

      const response = await axios.post(
        `http://127.0.0.1:8000/inspections/${inspectionId}/report`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log(
        "Report generated:",
        response.data
      );

      setReport(response.data);

    } catch (error) {
      console.error(
        "Report generation error:",
        error
      );

      // -------------------------------------------------------
      // REPORT ALREADY EXISTS
      // -------------------------------------------------------

      if (
        error.response &&
        error.response.status === 400 &&
        error.response.data.detail ===
          "Report already exists for this inspection"
      ) {
        try {
          console.log(
            "Report already exists. Loading existing report..."
          );

          const token =
            localStorage.getItem(
              "access_token"
            );

          const existingReport =
            await axios.get(
              `http://127.0.0.1:8000/inspections/${inspectionId}/report`,
              {
                headers: {
                  Authorization:
                    `Bearer ${token}`,
                },
              }
            );

          console.log(
            "Existing report:",
            existingReport.data
          );

          setReport(
            existingReport.data
          );

          return;

        } catch (loadError) {
          console.error(
            "Failed to load existing report:",
            loadError
          );

          if (loadError.response) {
            setError(
              loadError.response.data.detail ||
                "Failed to load existing report."
            );
          } else {
            setError(
              "Could not load existing report."
            );
          }

          return;
        }
      }

      // -------------------------------------------------------
      // OTHER ERRORS
      // -------------------------------------------------------

      if (error.response) {
        setError(
          error.response.data.detail ||
            "Failed to generate inspection report."
        );
      } else {
        setError(
          "Could not connect to backend."
        );
      }

    } finally {
      setGeneratingReport(false);
    }
  };

  // =========================================================
  // DOWNLOAD REPORT PDF
  // =========================================================

  const handleDownloadReport = async () => {
    try {
      setError("");

      const token =
        localStorage.getItem("access_token");

      console.log(
        "Downloading inspection report..."
      );

      const response = await axios.get(
        `http://127.0.0.1:8000/inspections/${inspectionId}/report/pdf`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
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

      console.log(
        "Inspection report downloaded successfully."
      );

    } catch (error) {
      console.error(
        "PDF download error:",
        error
      );

      setError(
        "Failed to download the inspection report."
      );
    }
  };

  // =========================================================
  // FORMAT FIELD NAME
  // =========================================================

  const formatFieldName = (field) => {
    return String(field)
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };

  // =========================================================
  // RENDER ANY VALUE SAFELY
  // =========================================================

  const renderValue = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return (
        <span className="empty-value">
          Not specified
        </span>
      );
    }

    if (typeof value === "string") {
      return <span>{value}</span>;
    }

    if (
      typeof value === "number" ||
      typeof value === "boolean"
    ) {
      return (
        <span>
          {String(value)}
        </span>
      );
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return (
          <span className="empty-value">
            None
          </span>
        );
      }

      return (
        <ul className="checklist-value-list">
          {value.map(
            (item, index) => (
              <li key={index}>
                {renderValue(item)}
              </li>
            )
          )}
        </ul>
      );
    }

    if (
      typeof value === "object"
    ) {
      return (
        <div className="checklist-nested-object">
          {Object.entries(value).map(
            ([key, nestedValue]) => (
              <div
                className="checklist-nested-field"
                key={key}
              >
                <strong>
                  {formatFieldName(key)}
                </strong>

                <div>
                  {renderValue(
                    nestedValue
                  )}
                </div>
              </div>
            )
          )}
        </div>
      );
    }

    return (
      <span>
        {String(value)}
      </span>
    );
  };

  // =========================================================
  // SELECTED CATEGORY NAME
  // =========================================================

  const selectedCategoryName =
    categories.find(
      (category) =>
        category.category_code ===
        selectedCategory
    )?.category_name ||
    selectedCategory;

  // =========================================================
  // CHECKLIST RULES
  // =========================================================

  const checklistRules =
    Array.isArray(
      checklist?.rules?.rules
    )
      ? checklist.rules.rules
      : [];

  // =========================================================
  // GET RULE CHECK ENTRIES
  // =========================================================

  const getRuleCheckEntries = (rule) => {
    if (
      !rule ||
      typeof rule !== "object"
    ) {
      return [];
    }

    const excludedFields = [
      "rule_id",
      "rule",
      "description",
      "product_type",
    ];

    return Object.entries(rule).filter(
      ([key]) =>
        !excludedFields.includes(key)
    );
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="inspection-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="inspection-header">

        <div>

          <button
            className="back-button"
            onClick={onBack}
          >
            ← Back
          </button>

          <h1>
            Inspection #{inspectionId}
          </h1>

          <p>
            Product Information Extraction &
            Compliance Evaluation
          </p>

        </div>

      </div>


      <div className="inspection-content">

        {/* ===================================================
            IMAGE UPLOAD
        =================================================== */}

        <div className="upload-card">

          <h2>
            Product Image
          </h2>

          <p>
            Upload a clear image of the
            packaged commodity.
          </p>

          <input
            type="file"
            accept="image/*"
            onChange={(e) =>
              setImage(
                e.target.files[0]
              )
            }
          />

          {image && (

            <div className="selected-image">

              <p>
                Selected: {image.name}
              </p>

              <img
                src={URL.createObjectURL(image)}
                alt="Product preview"
              />

            </div>

          )}

          <button
            className="primary-button"
            onClick={handleUpload}
            disabled={loading}
          >

            {loading
              ? "Analyzing Product..."
              : "Upload & Analyze"}

          </button>

        </div>


        {/* ===================================================
            ERROR
        =================================================== */}

        {error && (
          <div className="error">
            {error}
          </div>
        )}


        {/* ===================================================
            INSPECTOR VERIFICATION
        =================================================== */}

        {result && verifiedData && (

          <div className="verification-card">

            <div className="verification-header">

              <div>

                <h2>
                  Inspector Verification
                </h2>

                <p>
                  Review the information extracted
                  from the product image. Correct
                  any inaccurate values before
                  continuing.
                </p>

              </div>

              {verified && (
                <span className="verified-badge">
                  ✓ Verified
                </span>
              )}

            </div>


            {/* PRODUCT INFORMATION */}

            <h3>
              Product Information
            </h3>

            <div className="verification-grid">

              {Object.entries(
                verifiedData
              )
                .filter(
                  ([key]) =>
                    key !==
                      "consumer_care_details" &&
                    key !==
                      "other_declarations"
                )
                .map(
                  ([key, value]) => (

                    <div
                      className="verification-field"
                      key={key}
                    >

                      <label>
                        {formatFieldName(key)}
                      </label>

                      <input
                        type="text"
                        value={
                          typeof value ===
                            "string" ||
                          typeof value ===
                            "number"
                            ? value
                            : value == null
                            ? ""
                            : JSON.stringify(
                                value
                              )
                        }
                        placeholder="Not detected"
                        onChange={(e) =>
                          handleFieldChange(
                            key,
                            e.target.value
                          )
                        }
                      />

                    </div>

                  )
                )}

            </div>


            {/* CONSUMER CARE */}

            <h3>
              Consumer Care Details
            </h3>

            <div className="verification-grid">

              {verifiedData
                .consumer_care_details &&
                typeof verifiedData
                  .consumer_care_details ===
                  "object" &&
                Object.entries(
                  verifiedData
                    .consumer_care_details
                ).map(
                  ([key, value]) => (

                    <div
                      className="verification-field"
                      key={key}
                    >

                      <label>
                        {formatFieldName(key)}
                      </label>

                      <input
                        type="text"
                        value={
                          typeof value ===
                            "string" ||
                          typeof value ===
                            "number"
                            ? value
                            : value == null
                            ? ""
                            : JSON.stringify(
                                value
                              )
                        }
                        placeholder="Not detected"
                        onChange={(e) =>
                          handleConsumerCareChange(
                            key,
                            e.target.value
                          )
                        }
                      />

                    </div>

                  )
                )}

            </div>


            {/* OTHER DECLARATIONS */}

            <h3>
              Other Declarations
            </h3>

            <textarea
              className="declarations-input"
              value={
                Array.isArray(
                  verifiedData
                    .other_declarations
                )
                  ? verifiedData
                      .other_declarations
                      .join("\n")
                  : ""
              }
              placeholder="No other declarations detected"
              onChange={(e) => {

                setVerifiedData(
                  (previous) => ({
                    ...previous,
                    other_declarations:
                      e.target.value
                        .split("\n")
                        .filter(
                          (item) =>
                            item.trim() !== ""
                        ),
                  })
                );

                setVerified(false);
                setChecklist(null);
                setEvaluation(null);
                setReport(null);

              }}
            />


            {/* VERIFY */}

            <div className="verification-actions">

              <button
                className="verify-button"
                onClick={handleVerify}
                disabled={
                  loading ||
                  verified
                }
              >

                {loading
                  ? "Saving..."
                  : verified
                  ? "✓ Information Verified"
                  : "✓ Confirm & Verify Information"}

              </button>

            </div>


            {verified && (

              <div className="verification-success">

                <strong>
                  Product information verified
                </strong>

                <p>
                  The extracted information has
                  been reviewed by the inspector
                  and saved successfully. It is now
                  ready for compliance evaluation.
                </p>

              </div>

            )}

          </div>

        )}


        {/* ===================================================
            PRODUCT CATEGORY
        =================================================== */}

        {verified && (

          <div className="category-card">

            <div className="category-header">

              <div>

                <h2>
                  Product Category
                </h2>

                <p>
                  Select the product category to
                  determine the applicable compliance
                  checklist.
                </p>

              </div>

              <span className="step-badge">
                Step 2
              </span>

            </div>


            <select
              className="category-select"
              value={selectedCategory}
              disabled={!!checklist}
              onChange={(e) => {

                setSelectedCategory(
                  e.target.value
                );

                setChecklist(null);
                setEvaluation(null);
                setReport(null);
                setError("");

              }}
            >

              <option value="">
                Select product category
              </option>

              {categories.map(
                (category) => (

                  <option
                    key={
                      category.category_id
                    }
                    value={
                      category.category_code
                    }
                  >
                    {category.category_name}
                  </option>

                )
              )}

            </select>


            {selectedCategory && (

              <div className="selected-category">

                <span>
                  Selected category
                </span>

                <strong>
                  {selectedCategoryName}
                </strong>

              </div>

            )}


            {!checklist && (

              <div className="evaluation-actions">

                <button
                  className="evaluate-button"
                  onClick={
                    handleCreateChecklist
                  }
                  disabled={
                    creatingChecklist ||
                    !selectedCategory
                  }
                >

                  {creatingChecklist
                    ? "Generating Checklist..."
                    : "Generate Compliance Checklist"}

                </button>

              </div>

            )}

          </div>

        )}


        {/* ===================================================
            COMPLIANCE CHECKLIST
        =================================================== */}

        {checklist && (

          <div className="checklist-card">

            {/* HEADER */}

            <div className="checklist-header">

              <div>

                <h2>
                  Applicable Compliance Checklist
                </h2>

                <p>
                  Review all requirements that must
                  be checked for this product.
                </p>

              </div>

              <span className="step-badge">
                Step 3
              </span>

            </div>


            {/* CATEGORY */}

            <div className="checklist-category">

              <span>
                Product Category
              </span>

              <strong>
                {selectedCategoryName}
              </strong>

            </div>


            {/* RULES */}

            <div className="checklist-rules">

              {checklistRules.length > 0 ? (

                checklistRules.map(
                  (rule, index) => {

                    const checkEntries =
                      getRuleCheckEntries(
                        rule
                      );

                    return (

                      <div
                        className="checklist-rule"
                        key={
                          rule?.rule_id ??
                          index
                        }
                      >

                        {/* RULE NUMBER */}

                        <div className="checklist-rule-number">
                          {index + 1}
                        </div>


                        {/* RULE CONTENT */}

                        <div className="checklist-rule-content">

                          {/* RULE TITLE */}

                          <div className="checklist-rule-title">

                            <span className="rule-label">
                              COMPLIANCE RULE
                            </span>

                            <h3>
                              {rule?.rule_id
                                ? `Rule ${rule.rule_id}`
                                : `Rule ${index + 1}`}
                            </h3>

                          </div>


                          {/* DESCRIPTION */}

                          {rule?.description && (

                            <div className="rule-description">

                              <strong>
                                What this rule covers
                              </strong>

                              <p>
                                {renderValue(
                                  rule.description
                                )}
                              </p>

                            </div>

                          )}


                          {/* PRODUCT TYPE */}

                          {rule?.product_type && (

                            <div className="rule-info-box">

                              <strong>
                                Product Type
                              </strong>

                              <div>
                                {renderValue(
                                  rule.product_type
                                )}
                              </div>

                            </div>

                          )}


                          {/* ALL CHECKS */}

                          <div className="rule-checks-section">

                            <div className="rule-checks-header">

                              <div>

                                <span className="rule-label">
                                  INSPECTION REQUIREMENTS
                                </span>

                                <h4>
                                  What needs to be checked
                                </h4>

                              </div>

                            </div>


                            {checkEntries.length > 0 ? (

                              <div className="rule-check-list">

                                {checkEntries.map(
                                  ([key, value]) => (

                                    <div
                                      className="rule-check-item"
                                      key={key}
                                    >

                                      <div className="rule-check-icon">
                                        ✓
                                      </div>

                                      <div className="rule-check-content">

                                        <strong>
                                          {formatFieldName(
                                            key
                                          )}
                                        </strong>

                                        <div className="rule-check-value">

                                          {renderValue(
                                            value
                                          )}

                                        </div>

                                      </div>

                                    </div>

                                  )
                                )}

                              </div>

                            ) : (

                              <div className="empty-checks">

                                No specific checks
                                specified for this rule.

                              </div>

                            )}

                          </div>

                        </div>

                      </div>

                    );
                  }
                )

              ) : (

                <div className="empty-checks">
                  No checklist rules found.
                </div>

              )}

            </div>


            {/* EVALUATE BUTTON */}

            <div className="evaluation-actions">

              <button
                className="evaluate-button"
                onClick={handleEvaluate}
                disabled={
                  evaluating ||
                  !!evaluation
                }
              >

                {evaluating
                  ? "Evaluating Compliance..."
                  : evaluation
                  ? "✓ Evaluation Completed"
                  : "✓ Evaluate Compliance"}

              </button>

            </div>

          </div>

        )}


        {/* ===================================================
            EVALUATION RESULT
        =================================================== */}

        {evaluation && (

          <div className="evaluation-card">

            <div className="evaluation-header">

              <div>

                <h2>
                  Compliance Evaluation
                </h2>

                <p>
                  AI-powered evaluation based on
                  the selected product category
                  and applicable Legal Metrology
                  rules.
                </p>

              </div>


              <div
                className={
                  evaluation.overall_status ===
                  "PASS"
                    ? "evaluation-status pass"
                    : "evaluation-status fail"
                }
              >

                {evaluation.overall_status}

              </div>

            </div>


            {/* CATEGORY */}

            <div className="evaluation-category">

              <span>
                Product Category
              </span>

              <strong>
                {selectedCategoryName}
              </strong>

            </div>


            {/* RULE RESULTS */}

            <h3>
              Rule Evaluation Results
            </h3>


            <div className="rule-results">

              {Array.isArray(
                evaluation.rule_evaluations
              ) &&
                evaluation.rule_evaluations.map(
                  (rule, index) => (

                    <div
                      className="rule-result"
                      key={
                        rule?.rule_id ??
                        index
                      }
                    >

                      <div className="rule-result-header">

                        <strong>
                          Rule{" "}
                          {rule?.rule_id ??
                            index + 1}
                        </strong>


                        <span
                          className={
                            rule?.status ===
                            "PASS"
                              ? "rule-status pass"
                              : "rule-status fail"
                          }
                        >

                          {rule?.status ||
                            "UNKNOWN"}

                        </span>

                      </div>


                      <div className="rule-detail">

                        <strong>
                          Evidence
                        </strong>

                        <div>
                          {renderValue(
                            rule?.evidence ||
                              "No evidence provided."
                          )}
                        </div>

                      </div>


                      <div className="rule-detail">

                        <strong>
                          Details
                        </strong>

                        <div>
                          {renderValue(
                            rule?.details ||
                              "No additional details."
                          )}
                        </div>

                      </div>

                    </div>

                  )
                )}

            </div>


            {/* =================================================
                REPORT SECTION
                ================================================= */}

            <div className="report-actions">

              {!report ? (

                <button
                  className="generate-report-button"
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                >

                  {generatingReport
                    ? "Generating Report..."
                    : "📄 Generate Inspection Report"}

                </button>

              ) : (

                <div className="report-ready">

                  <div className="report-ready-content">

                    <div className="report-icon">
                      ✓
                    </div>

                    <div>

                      <strong>
                        Inspection Report Ready
                      </strong>

                      <p>
                        The compliance report has
                        been generated successfully.
                      </p>

                    </div>

                  </div>


                  <button
                    className="download-report-button"
                    onClick={handleDownloadReport}
                  >
                    ↓ Download PDF Report
                  </button>

                </div>

              )}

            </div>

          </div>

        )}

      </div>

    </div>
  );
}

export default Inspection;