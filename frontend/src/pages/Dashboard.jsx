import React, { useEffect, useMemo, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all"); // all | solved | unsolved
  const [collapsed, setCollapsed] = useState({});

  useEffect(() => {
    loadQuestions();
  }, []);

  async function loadQuestions() {
    setLoading(true);
    setError("");
    try {
      const res = await api.get("/questions");
      setCategories(res.data);
    } catch (err) {
      setError("Failed to load questions. Is the backend running and seeded?");
    } finally {
      setLoading(false);
    }
  }

  async function toggleQuestion(categoryName, questionId, currentSolved) {
    // optimistic update
    setCategories((prev) =>
      prev.map((cat) => {
        if (cat.category !== categoryName) return cat;
        const questions = cat.questions.map((q) =>
          q.id === questionId ? { ...q, solved: !currentSolved } : q
        );
        const solved = questions.filter((q) => q.solved).length;
        return { ...cat, questions, solved };
      })
    );

    try {
      await api.put(`/progress/${questionId}`, { solved: !currentSolved });
    } catch (err) {
      // revert on failure
      loadQuestions();
    }
  }

  const totals = useMemo(() => {
    const total = categories.reduce((sum, c) => sum + c.total, 0);
    const solved = categories.reduce((sum, c) => sum + c.solved, 0);
    return { total, solved };
  }, [categories]);

  function toggleCollapse(category) {
    setCollapsed((prev) => ({ ...prev, [category]: !prev[category] }));
  }

  if (loading) return <div className="center-message">Loading questions...</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>DSA Tracker</h1>
          {user && <p className="welcome">Hi, {user.name}</p>}
        </div>
        <button className="logout-btn" onClick={logout}>
          Log out
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="progress-summary">
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: totals.total
                ? `${(totals.solved / totals.total) * 100}%`
                : "0%",
            }}
          />
        </div>
        <span>
          {totals.solved} / {totals.total} solved
        </span>
      </div>

      <div className="filter-row">
        {["all", "solved", "unsolved"].map((f) => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? "active" : ""}`}
            onClick={() => setFilter(f)}
          >
            {f[0].toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {categories.length === 0 && !error && (
        <div className="center-message">
          No questions found. Run the backend seed script to load questions.
        </div>
      )}

      <div className="category-list">
        {categories.map((cat) => {
          const visibleQuestions = cat.questions.filter((q) => {
            if (filter === "solved") return q.solved;
            if (filter === "unsolved") return !q.solved;
            return true;
          });
          if (visibleQuestions.length === 0) return null;

          const isCollapsed = collapsed[cat.category];

          return (
            <div className="category-card" key={cat.category}>
              <button
                className="category-header"
                onClick={() => toggleCollapse(cat.category)}
              >
                <span>{cat.category}</span>
                <span className="category-count">
                  {cat.solved}/{cat.total}
                </span>
              </button>

              {!isCollapsed && (
                <ul className="question-list">
                  {visibleQuestions.map((q) => (
                    <li key={q.id} className="question-row">
                      <label className="question-checkbox">
                        <input
                          type="checkbox"
                          checked={q.solved}
                          onChange={() =>
                            toggleQuestion(cat.category, q.id, q.solved)
                          }
                        />
                        <span className={q.solved ? "solved-title" : ""}>
                          {q.title}
                        </span>
                      </label>
                      {q.url && (
                        <a
                          href={q.url}
                          target="_blank"
                          rel="noreferrer"
                          className="question-link"
                        >
                          Open ↗
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
