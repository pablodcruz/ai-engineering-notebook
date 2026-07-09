const labs = [
  {
    title: "Prompt Engineering Lab",
    signal: "Structured outputs",
    summary: "Turns vague prompts into task-specific workflows with constraints and comparison notes.",
  },
  {
    title: "RAG Lab",
    signal: "Grounded answers",
    summary: "Builds a retrieval pipeline, inspects chunks, returns citations, and handles missing coverage.",
  },
  {
    title: "API And SDK Integration Lab",
    signal: "Environment readiness",
    summary: "Separates credential, runtime, endpoint, and parsing failures from model behavior.",
  },
  {
    title: "Agents Tool-Use Lab",
    signal: "Constrained autonomy",
    summary: "Defines narrow tools, logs observations, and enforces permissions and stop conditions.",
  },
  {
    title: "Troubleshooting Drills",
    signal: "Operational judgment",
    summary: "Practices timed debugging for credentials, environments, retrieval, output format, and loops.",
  },
  {
    title: "StreamFlow Phase 1",
    signal: "Data engineering",
    summary: "Frames Kafka-compatible streaming, Spark processing, Airflow orchestration, and data quality checks.",
  },
];

const list = document.querySelector("#lab-list");

if (list) {
  list.innerHTML = labs
    .map(
      (lab) => `
        <article class="lab-item">
          <div>
            <h3>${lab.title}</h3>
            <p>${lab.summary}</p>
          </div>
          <span>${lab.signal}</span>
        </article>
      `,
    )
    .join("");
}
