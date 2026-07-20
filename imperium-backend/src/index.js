const express = require("express");
const app = express();

app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

app.listen(4000, () => {
  console.log("Backend listening on port 4000");
});
