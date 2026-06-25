import 'package:flutter/material.dart';
void main() => runApp(const MyApp());
class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'A1OS',
      home: Scaffold(
        appBar: AppBar(title: Text('A1OS')),
        body: Center(child: Text('A1OS Mobile')),
      ),
    );
  }
}
