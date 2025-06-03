<?php
$servername = "localhost";  // Change as per your DB server
$username = "root";         // Your MySQL username
$password = "";             // Your MySQL password
$dbname = "crm";            // Your database name

// Create a connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to fetch all rows from the 'customers' table
function get_customers($conn) {
    $sql = "SELECT * FROM customers";
    $result = $conn->query($sql);
    return $result;
}

// Handling form submissions for adding or modifying data
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['add_column'])) {
        $column_name = $_POST['column_name'];
        $column_type = $_POST['column_type'];
        $add_sql = "ALTER TABLE customers ADD COLUMN $column_name $column_type";
        if ($conn->query($add_sql) === TRUE) {
            echo "Column $column_name added successfully!";
        } else {
            echo "Error adding column: " . $conn->error;
        }
    }

    // More operations like Update, Delete can be handled similarly
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Management</title>
</head>
<body>
    <h1>Manage Database</h1>

    <!-- Form to Add Column -->
    <h2>Add Column to 'customers' Table</h2>
    <form action="database_manage.php" method="POST">
        <label for="column_name">Column Name:</label>
        <input type="text" name="column_name" required><br><br>
        <label for="column_type">Column Type:</label>
        <input type="text" name="column_type" required><br><br>
        <input type="submit" name="add_column" value="Add Column">
    </form>

    <h2>Current Data in 'customers' Table</h2>
    <table border="1">
        <thead>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Accessible Pages</th>
                <th>Failed Attempts</th>
                <th>Lock Until</th>
                <th>Last Download Date</th>
                <th>Reference Name</th>
                <!-- Add other column headers dynamically if required -->
            </tr>
        </thead>
        <tbody>
            <?php
            $customers = get_customers($conn);
            if ($customers->num_rows > 0) {
                while($row = $customers->fetch_assoc()) {
                    echo "<tr>";
                    echo "<td>" . $row["id"] . "</td>";
                    echo "<td>" . $row["username"] . "</td>";
                    echo "<td>" . $row["email"] . "</td>";
                    echo "<td>" . $row["accessible_pages"] . "</td>";
                    echo "<td>" . $row["failed_attempts"] . "</td>";
                    echo "<td>" . $row["lock_until"] . "</td>";
                    echo "<td>" . $row["last_download_date"] . "</td>";
                    echo "<td>" . $row["reference_name"] . "</td>";
                    // Add other columns dynamically if required
                    echo "</tr>";
                }
            } else {
                echo "<tr><td colspan='8'>No data found</td></tr>";
            }
            ?>
        </tbody>
    </table>

</body>
</html>

<?php
// Close the connection
$conn->close();
?>
