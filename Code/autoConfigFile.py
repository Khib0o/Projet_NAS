import jinja2

template_file = 'router_template.txt'
output_dir = 'configs'

# Define the router data
routers = [
    {'hostname': 'R1', 'ip': '192.168.1.1', 'mask': '255.255.255.0'},
    {'hostname': 'R2', 'ip': '192.168.1.2', 'mask': '255.255.255.0'},
    {'hostname': 'R3', 'ip': '192.168.1.3', 'mask': '255.255.255.0'}
]

# Load the template
with open(template_file, 'r') as f:
    template = jinja2.Template(f.read())

# Generate the config files
for router in routers:
    config = template.render(router=router)
    with open(f'{output_dir}/{router["hostname"]}.cfg', 'w') as f:
        f.write(config)

print("config files have been generated")
