function getDatabaseInfoById(databaseId) {
  // Create an object to store database information
  const databaseInfo = {
    name: document.querySelector(`td[data-db-name="${databaseId}"]`).textContent.trim(),
    displayName: document.querySelector(`td[data-display-name="${databaseId}"]`).textContent.trim(),
    type: document.querySelector(`td[data-db-type="${databaseId}"]`).textContent.trim(),
    host: document.querySelector(`td[data-db-host="${databaseId}"]`).textContent.trim(),
    port: document.querySelector(`td[data-db-port="${databaseId}"]`).textContent.trim(),
    group: document.querySelector(`td[data-db-group="${databaseId}"]`).textContent.trim(),
    user: document.querySelector(`td[data-db-user="${databaseId}"]`).textContent.trim()
  };

  return databaseInfo;
}

function populateDatabaseFormForEdit(databaseId) {

  const modal = new bootstrap.Modal(document.getElementById('addDatabaseModal'));
  modal.show();

  const databaseInfo = getDatabaseInfoById(databaseId);

  document.getElementById('id_type').value = databaseInfo.type;
  document.getElementById('id_name').value = databaseInfo.name;
  document.getElementById('id_display_name').value = databaseInfo.displayName;

  document.getElementById('id_host').value = databaseInfo.host;
  document.getElementById('id_port').value = databaseInfo.port;
  document.getElementById("id_username").value = databaseInfo.user;
  document.getElementById("db_id").value = databaseId

}