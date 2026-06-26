import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(A1OSApp());

class A1OSApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'A1OS',
    theme: ThemeData.dark(),
    home: Dashboard(),
  );
}

class Dashboard extends StatefulWidget {
  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  var data = {};
  final apiKey = 'e6d4f897ff9934ed5d61309bf1286436f96c0dd55a9c7b42b921c2936011267d';

  @override
  void initState() {
    super.initState();
    fetchStatus();
  }

  Future<void> fetchStatus() async {
    try {
      final res = await http.get(
        Uri.parse('http://localhost:8086/system/status'),
        headers: {'X-API-Key': apiKey},
      );
      setState(() => data = jsonDecode(res.body));
    } catch(e) { print(e); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text('A1OS v2.0')),
    body: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text('Status: ${data['status'] ?? 'loading...'}'),
          Text('Version: ${data['version'] ?? '...'}'),
          Text('Modules: ${(data['modules'] ?? []).join(', ')}'),
        ],
      ),
    ),
  );
}
