import 'package:equatable/equatable.dart';

abstract class RecEvent extends Equatable {
  const RecEvent();
  @override
  List<Object?> get props => [];
}

class LoadInitial extends RecEvent {}

class SendFeedback extends RecEvent {
  final String id;
  final String action; // "like" or "dislike"
  const SendFeedback({required this.id, required this.action});
  @override
  List<Object?> get props => [id, action];
}
