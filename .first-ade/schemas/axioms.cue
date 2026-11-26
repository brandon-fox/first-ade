package schemas

close({
	version: "0.1"
	project: string & !=""
	unscoped_max_files: int & >=1 | *3
	tamper_guard: close({
		id:      "ADE-AX-01"
		enabled: bool
		protected_paths: [...string]
	})
	boundary_guard: close({
		id:      "ADE-AX-02"
		enabled: bool
		engine:  "import-linter"
		config:  string & !=""
	})
	coupling_guard: close({
		id:      "ADE-AX-03"
		enabled: bool
		rules: [...close({
			name: string & !=""
			if_changed: [...string]
			then_require: [...string]
		})]
	})
	ast_guard: close({
		id:        "ADE-AX-04"
		enabled:   bool
		engine:    "ast-grep"
		rules_dir: string & !=""
		target_paths: [...string]
	})
})
