import 'package:equatable/equatable.dart';
import '../models/listing.dart';

enum RecStatus { initial, loading, success, failure }

class RecState extends Equatable {
  final RecStatus status;
  final Listing? current;
  final Listing? next;
  final String? error;

  const RecState({
    this.status = RecStatus.initial,
    this.current,
    this.next,
    this.error,
  });

  RecState copyWith({
    RecStatus? status,
    Listing? current,
    Listing? next,
    String? error,
  }) {
    return RecState(
      status: status ?? this.status,
      current: current ?? this.current,
      next: next ?? this.next,
      error: error ?? this.error,
    );
  }

  @override
  List<Object?> get props => [status, current, next, error];
}
