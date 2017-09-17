<!DOCTYPE html>
<html>
<head>
	<title>Riwayat Absensi Pegawai</title>
	<link rel="stylesheet" type="text/css" href="styles/styles.css">
	<link rel="stylesheet" type="text/css" href="styles/bootstrap.css">
</head>
<body>
	<div class="container"><br>
	<h1>Riwayat Absensi Pegawai</h1>
	<p>Sistem Absensi Pegawai dengan Face Recognition Menggunakan Metode LBPH Berbasis Raspberry Pi</p>
	<hr>
	<a class="btn btn-primary" href="datapegawai.php" role="button">Lihat Data Pegawai</a>
	<hr>
	<h2>Data Absensi</h2>
	<?php
	  try
	  {
		//open the database
		$db = new PDO('sqlite:facebase');

		//now output the data to a simple html table...
		print "<table border=1>";
		print "<tr><td>No.</td><td>ID Pegawai</td><td>Nama</td><td>Tanggal</td>
				<td>Waktu Masuk</td><td>Foto Masuk</td><td>Waktu Keluar</td><td>Foto Keluar</td></tr>";
		$result = $db->query('SELECT * FROM dataabsensi');
		foreach($result as $row)
		{
		  print "<tr><td>".$row['LogId']."</td>";
		  print "<td>".$row['id']."</td>";
		  print "<td>".$row['nama']."</td>";
		  print "<td>".$row['tanggal']."</td>";
		  print "<td>".$row['waktu_masuk']."</td>";
		  print "<td><img src='foto/".$row['foto_masuk']."'></td>";
		  print "<td>".$row['waktu_keluar']."</td>";
		  print "<td><img src='foto/".$row['foto_keluar']."'></td>";
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

