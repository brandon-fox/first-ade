package schemas

close({
	version: "0.1"
	task:    string & !=""
	allowed_paths: [...string]
	forbidden_paths?: [...string]
	waivers?: [...close({
		axiom_id:    string & !=""
		reason:      string & !=""
		approved_by: string & !=""
	})]
})
