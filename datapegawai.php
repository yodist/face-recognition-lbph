<!DOCTYPE html>
<html>
<head>
	<title>Riwayat Absensi Pegawai - Data Pegawai</title>
	<link rel="stylesheet" type="text/css" href="styles/styles.css">
	<link rel="stylesheet" type="text/css" href="styles/bootstrap.css">
</head>
<body>
	<div class="container"><br>
	<h1>Riwayat Absensi Pegawai</h1>
	<p>Sistem Absensi Pegawai dengan Face Recognition Menggunakan Metode LBPH Berbasis Raspberry Pi</p>
	<hr>
	<a class="btn btn-primary" href="index.php" role="button">Lihat Data Absensi</a>
	<hr>
	<h2>Data Pegawai</h2>
	<?php
	  try
	  {
		//open the database
		$db = new PDO('sqlite:facebase');

		//now output the data to a simple html table...
		print "<table border=1>";
		print "<tr><td>ID Pegawai</td><td>Foto</td><td>Nama</td><td>Jenis Kelamin</td><td>Jabatan</td><td>No. Telp</td></tr>";
		$result = $db->query('SELECT * FROM pegawai');
		foreach($result as $row)
		{
		  print "<tr><td>".$row['id']."</td>";
		  print "<td><img src='foto/".$row['foto_pegawai'].".jpg'></td>";
		  print "<td>".$row['nama']."</td>";
		  print "<td>".$row['jenis_kelamin']."</td>";
		  print "<td>".$row['jabatan']."</td>";
		  print "<td>".$row['no_telp']."</td>";
		}
		print "</table>";

		// close the database connection
		$db = NULL;
	  }
		catch(PDOException $e)
	  {
		print 'Exception : '.$e->getMessage();
	  }
	?>
	</div>
</body>
</html>

