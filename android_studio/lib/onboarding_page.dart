// lib/ui/onboarding_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../data/api_services.dart';
import '../bloc/rec_bloc.dart';
import '../bloc/rec_event.dart';
import 'home_page.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final _homeTypes = <String>{"Apartment", "Condo", "House"};
  final _styles = <String>{"modern", "spanish", "victorian", "cabin"};
  final _chosenHomeTypes = <String>{};
  final _chosenStyles = <String>{};
  final _cityCtrl = TextEditingController(text: "Santa Cruz");

  double _sqft = 1000;
  double _budget = 800000;

  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _cityCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final api = context.read<RecBloc>().api; // expose api in bloc below

    return Scaffold(
      appBar: AppBar(
        title: const Text("Your Preferences"),
        backgroundColor: const Color(0xFF8D6E63), // light brown
      ),
      body: AbsorbPointer(
        absorbing: _loading,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text("Home Type", style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _homeTypes.map((t) {
                final selected = _chosenHomeTypes.contains(t);
                return FilterChip(
                  label: Text(t),
                  selected: selected,
                  onSelected: (val) {
                    setState(() {
                      if (val) _chosenHomeTypes.add(t);
                      else _chosenHomeTypes.remove(t);
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            Text("Style", style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _styles.map((s) {
                final selected = _chosenStyles.contains(s);
                return FilterChip(
                  label: Text(s),
                  selected: selected,
                  onSelected: (val) {
                    setState(() {
                      if (val) _chosenStyles.add(s);
                      else _chosenStyles.remove(s);
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            Text("Location (City)"),
            const SizedBox(height: 8),
            TextField(
              controller: _cityCtrl,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: "e.g., Santa Cruz",
              ),
            ),
            const SizedBox(height: 16),

            Text("Minimum Square Feet: ${_sqft.toInt()}"),
            Slider(
              value: _sqft,
              min: 300,
              max: 4000,
              divisions: 37,
              label: _sqft.toInt().toString(),
              onChanged: (v) => setState(() => _sqft = v),
            ),
            const SizedBox(height: 8),

            Text("Budget: \$${_budget.toInt()}"),
            Slider(
              value: _budget,
              min: 50000,
              max: 3000000,
              divisions: 59,
              label: _budget.toInt().toString(),
              onChanged: (v) => setState(() => _budget = v),
            ),
            const SizedBox(height: 16),

            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),

            FilledButton(
              onPressed: () async {
                setState(() {
                  _loading = true;
                  _error = null;
                });
                try {
                  if (_chosenHomeTypes.isEmpty) {
                    throw Exception("Pick at least one home type");
                  }
                  if (_chosenStyles.isEmpty) {
                    throw Exception("Pick at least one style");
                  }
                  await api.setConstraints(
                    homeType: _chosenHomeTypes,
                    style: _chosenStyles,
                    location: _cityCtrl.text.trim(),
                    squareFeet: _sqft.toInt(),
                    budget: _budget.toInt(),
                  );
                  // Now that constraints are saved, load the feed
                  context.read<RecBloc>().add(LoadInitial());
                  if (!mounted) return;
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (_) => const HomePage()),
                  );
                } catch (e) {
                  setState(() => _error = e.toString());
                } finally {
                  if (mounted) setState(() => _loading = false);
                }
              },
              child: _loading
                  ? const SizedBox(
                  height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text("Continue"),
            ),
          ],
        ),
      ),
    );
  }
}
