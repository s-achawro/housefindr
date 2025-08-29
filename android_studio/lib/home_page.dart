import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/rec_bloc.dart';
import '../bloc/rec_state.dart';
import '../bloc/rec_event.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("House Recs"), backgroundColor:  const Color(0xFFDEB887),),
      body: BlocBuilder<RecBloc, RecState>(
        builder: (context, state) {
          if (state.status == RecStatus.loading && state.current == null) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.status == RecStatus.failure && state.current == null) {
            return Center(child: Text("Error: ${state.error}"));
          }
          if (state.current == null || state.current!.id.isEmpty) {
            return const Center(child: Text("No homes available"));
          }

          final cur = state.current!;
          return Center(
              child: Padding(
            padding: const EdgeInsets.all(16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Card(
                color: const Color(0xFFF5DEB3),
                margin: EdgeInsets.zero,
                elevation: 2,
                child: AspectRatio(
                  aspectRatio: 9 / 17,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // BACKGROUND IMAGE
                      if ((cur.imageUrl ?? '').isNotEmpty)
                        Image.network(
                          cur.imageUrl!,
                          fit: BoxFit.fitWidth,
                          errorBuilder: (_, __, ___) =>
                              Container(color: Colors.grey.shade300),
                        )
                      else
                        Container(color: Colors.grey.shade300),

                      // GRADIENT OVERLAY (for text readability)
                      Container(
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            stops: [0.4, 1.0],
                            colors: [Colors.transparent, Colors.black54],
                          ),
                        ),
                      ),

                      // TEXT + BUTTONS OVERLAY
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.end,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Title
                            Text(
                              cur.address ?? cur.city ?? "Unknown",
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 8),
                            // Details row
                            Text(
                              "Beds: ${cur.beds ?? '-'} | Baths: ${cur.baths ?? '-'}",
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.white70,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              "Sqft: ${cur.sqft ?? '-'} | \$${cur.price ?? '-'}",
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.white70,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              cur.tenure == "buy"
                                  ? "For Sale"
                                  : cur.tenure == "rent"
                                  ? "For Rent"
                                  : "Tenure: -",
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.white70,
                              ),
                            ),
                            const SizedBox(height: 12),

                            // Buttons
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                              children: [
                                ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white.withOpacity(0.9),
                                    foregroundColor: Colors.black87,
                                  ),
                                  onPressed: () {
                                    context.read<RecBloc>().add(
                                      SendFeedback(id: cur.id, action: "dislike"),
                                    );
                                  },
                                  icon: const Icon(Icons.close),
                                  label: const Text("Dislike"),
                                ),
                                ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.redAccent.withOpacity(0.9),
                                    foregroundColor: Colors.white,
                                  ),
                                  onPressed: () {
                                    context.read<RecBloc>().add(
                                      SendFeedback(id: cur.id, action: "like"),
                                    );
                                  },
                                  icon: const Icon(Icons.favorite),
                                  label: const Text("Like"),
                                ),
                              ],
                            ),

                            if (state.status == RecStatus.loading) ...[
                              const SizedBox(height: 12),
                              const LinearProgressIndicator(),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
              ),
          );
        },
      ),
    );
  }
}
