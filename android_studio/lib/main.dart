import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'data/api_services.dart';
import 'bloc/rec_bloc.dart';
import 'home_page.dart';
import 'onboarding_page.dart';
import 'bloc/rec_event.dart';

void main() {
  runApp(
    BlocProvider(
      create: (_) => RecBloc(ApiService()),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'House Recs',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
      ),
      // goes to OnboardingPage first (to set user preferences)
      home: const OnboardingPage(),
    );
  }
}