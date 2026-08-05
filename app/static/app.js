function render(info) {
  const rows = [
    ["Hostname", info.hostname],
    ["Server IP", info.server_ip],
    ["Pod name", info.pod_name],
    ["Pod IP", info.pod_ip],
    ["Node name", info.node_name],
    ["Node IP", info.node_ip],
    ["Request #", info.request_id],
    ["Client IP", info.client_ip],
    ["AWS instance", info.aws.instance_id],
    ["AWS AZ", info.aws.availability_zone],
    ["AWS private IP", info.aws.private_ip],
    ["AWS public IP", info.aws.public_ip],
    ["AWS type", info.aws.instance_type],
    ["AWS AMI", info.aws.ami_id],
    ["AWS hostname", info.aws.local_hostname],
  ];
  const dl = document.getElementById("fields");
  dl.innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v ?? "n/a"}</dd>`).join("");
}

async function refresh() {
  const res = await fetch("/api/info");
  render(await res.json());
}

document.getElementById("refresh").addEventListener("click", refresh);
render(window.__BOOT__);
setInterval(refresh, 3000);