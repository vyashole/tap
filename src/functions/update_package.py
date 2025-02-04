def update_package(mpr_url, application_name, application_version):
	import os
	import json
	import requests

	from functions.install_package import install_package    # REMOVE AT PACKAGING

	# Get MPR packages and their respective versions
	package_list = os.popen("dpkg-query --show --showformat '${Package}/${MPR-Package}/${Version}\n' | grep '^[^/]*/[^/]'").read()

	request_packages_temp = []

	for i in package_list.rstrip().splitlines():
		request_packages_temp += [i.split('/')[1] + '/' + i.split('/')[2]]

	request_packages = sorted(request_packages_temp)
	local_packages_number = len(request_packages)

	rpc_request_arguments = ""

	for i in request_packages:
		rpc_request_arguments += "&arg[]=" + i.split('/')[0]

	mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=info{rpc_request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})

	try:
		mpr_rpc_json_data = json.loads(mpr_rpc_request.text)

	except json.decoder.JSONDecodeError:
		print("[JSON] There was an error processing your request.")
		quit(1)

	if mpr_rpc_json_data['resultcount'] == 0:
		printf("No updates available.")
		quit(1)

	# Check for updates
	resultcount = mpr_rpc_json_data['resultcount'] - 1
	number = 0
	to_update = []

	while number <= resultcount:
		# Get name and version
		rpc_package_name = mpr_rpc_json_data['results'][number]['Name']
		rpc_package_version = mpr_rpc_json_data['results'][number]['Version']

		# Find array number for matching local package
		number2 = 0
		while number2 < local_packages_number:

			local_package_name = request_packages[number2].split('/')[0]

			if local_package_name == rpc_package_name:
				local_package_version = request_packages[number2].split('/')[1]
				break

			number2 = number2 + 1

		if local_package_version != rpc_package_version:
			to_update += [rpc_package_name]

		number = number + 1

	if len(to_update) == 0:
		print("No updates available.")
		quit(0)

	install_package(mpr_url, to_update, "upgraded", application_name, application_version)
