import sys
import os


def generate_docker_compose(service_count, game_mode, start_from, template_file, output_file):
    with open(template_file, 'r') as file:
        template = file.read()

    services = []
    services.append('services:')
    for i in range(service_count):
        service_name = f'{game_mode}{i + 1}'
        udp_port = start_from + i
        tcp_port = start_from + i
        rcon_port = start_from + i + 1000

        service = template.replace('{SERVICE_NAME}', service_name)
        service = service.replace('{NET_PORT}:{NET_PORT}/udp', f'{udp_port}:{udp_port}/udp')
        service = service.replace('{NET_PORT}:{NET_PORT}/tcp', f'{tcp_port}:{udp_port}/tcp')
        service = service.replace('{RCON_PORT}:{RCON_PORT}', f'{rcon_port}:{rcon_port}')
        service = service.replace('NET_PORT={NET_PORT}', f'NET_PORT={udp_port}')
        service = service.replace('ZMQ_STATS_PORT={NET_PORT}', f'ZMQ_STATS_PORT={udp_port}')
        service = service.replace('ZMQ_RCON_PORT={RCON_PORT}', f'ZMQ_RCON_PORT={rcon_port}')
        service = service.replace('{IDX}', f'{i + 1}')
        indented_service = "\n".join(["  " + line if line else line for line in service.split('\n')])
        services.append(indented_service)

    with open(output_file, 'w') as file:
        for index, service in enumerate(services):
            if index > 0:
                file.write('\n')
            file.write(service)
            file.write('\n')


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Usage: python generate_docker_compose.py <service_count> <service_type> <start_from> <template_file> <output_file>")
        sys.exit(1)

    service_count = int(sys.argv[1])
    service_type = sys.argv[2]
    start_from = int(sys.argv[3])
    template_file = sys.argv[4]
    output_file = sys.argv[5]

    if not os.path.isfile(template_file):
        print(f"Template file {template_file} does not exist.")
        sys.exit(1)

    generate_docker_compose(service_count, service_type, start_from, template_file, output_file)
