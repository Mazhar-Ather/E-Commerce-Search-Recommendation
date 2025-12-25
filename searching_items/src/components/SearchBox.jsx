import { useState } from "react";

function SearchBox({ onInputChange, suggestions }) {
  const [searchTerm, setSearchTerm] = useState("");

  const handleChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    onInputChange(value); // 🔥 THIS WAS MISSING
  };

  return (
   <div
  style={{
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #667eea, #764ba2)"
  }}
>
  <div
    style={{
      background: "#ffffff",
      padding: "30px",
      width: "340px",
      borderRadius: "12px",
      boxShadow: "0 15px 30px rgba(0,0,0,0.2)",
      textAlign: "center"
    }}
  >
    <h2 style={{ marginBottom: "20px", color: "#333" }}>
      🔍 Product Search
    </h2>

    <input
      type="text"
      placeholder="Enter product name..."
      value={searchTerm}
      onChange={handleChange}
      style={{
        width: "100%",
        padding: "12px",
        fontSize: "15px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        outline: "none",
        marginBottom: "10px"
      }}
    />

    {/* 🔥 Suggestions Dropdown */}
    {suggestions.length > 0 && (
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          margin: 0,
          maxHeight: "150px",
          overflowY: "auto",
          border: "1px solid #ddd",
          borderRadius: "8px",
          textAlign: "left"
        }}
      >
        {suggestions.map((item, index) => (
          <li
            key={index}
            style={{
              padding: "10px",
              cursor: "pointer",
              borderBottom: "1px solid #eee",
              transition: "background 0.2s"
            }}
            onMouseOver={(e) =>
              (e.target.style.background = "#f1f1f1")
            }
            onMouseOut={(e) =>
              (e.target.style.background = "transparent")
            }
            onClick={() => setSearchTerm(item)}
          >
            {item}
          </li>
        ))}
      </ul>
    )}

    <button
      style={{
        marginTop: "20px",
        width: "100%",
        padding: "12px",
        fontSize: "16px",
        fontWeight: "bold",
        color: "#fff",
        background: "#667eea",
        border: "none",
        borderRadius: "8px",
        cursor: "pointer",
        transition: "background 0.3s"
      }}
      onMouseOver={(e) =>
        (e.target.style.background = "#5a67d8")
      }
      onMouseOut={(e) =>
        (e.target.style.background = "#667eea")
      }
    >
      Search
    </button>
  </div>
</div>

  );
}

export default SearchBox;
