local:
	#mkdir -p tmp
	#npm install && npm update
	npx antora --stacktrace --log-format=pretty lh-local-playbook.yml 2>&1 | tee tmp/local-build.log 2>&1

netlify:
	mkdir -p tmp
	npm install && npm update
	npx antora --stacktrace --log-format=pretty lh-netlify-playbook.yml 2>&1 | tee tmp/netlify-build.log 2>&1

gen_nav:
	bin/gen_lh_nav
