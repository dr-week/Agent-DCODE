// Agent-DCODE In-Browser Offline & Demo Simulator for GitHub Pages
// Intercepts fetch requests when running on static hosting without a live backend

(function() {
    const MOCK_FILES = [
        { name: "src", type: "folder", children: [
            { name: "dcode", type: "folder", children: [
                { name: "agent.py", type: "file", status: "clean" },
                { name: "harness.py", type: "file", status: "verified" },
                { name: "quantum.py", type: "file", status: "clean" }
            ]}
        ]},
        { name: "evals", type: "folder", children: [
            { name: "swe_bench_mini.json", type: "file", status: "clean" }
        ]}
    ];

    window.simulateAgentRun = function(task) {
        return {
            success: true,
            plan: [
                "1. Analyze repository AST and identify target symbols",
                "2. Apply surgical patch using PatchResolver",
                "3. Execute test verification and check regression"
            ],
            actions: [
                { type: "search_code", query: task, status: "completed" },
                { type: "replace_in_file", target: "old_logic()", replacement: "optimized_logic()", status: "completed" },
                { type: "run_python", code: "assert True", output: "ALL_PASS", status: "completed" }
            ],
            results: [
                { check: "Syntax AST Gate", status: "PASSED" },
                { check: "Regression Detection", status: "CLEAN_NO_REGRESSIONS" },
                { check: "Harness Scorecard", status: "Pass@1 (100%)" }
            ]
        };
    };
})();
