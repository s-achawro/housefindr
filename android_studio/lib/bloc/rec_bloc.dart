import 'package:flutter_bloc/flutter_bloc.dart';
import 'rec_event.dart';
import 'rec_state.dart';
import '../data/api_services.dart';

class RecBloc extends Bloc<RecEvent, RecState> {
  final ApiService api;
  ApiService get apiService => api; // optional alias


  RecBloc(this.api) : super(const RecState()) {
    on<LoadInitial>(_onLoadInitial);
    on<SendFeedback>(_onSendFeedback);
  }

  Future<void> _onLoadInitial(LoadInitial event, Emitter<RecState> emit) async {
    emit(state.copyWith(status: RecStatus.loading));
    try {
      final pair = await api.initFeed();
      emit(state.copyWith(
        status: RecStatus.success,
        current: pair.$1,
        next: pair.$2,
      ));
    } catch (e) {
      emit(state.copyWith(status: RecStatus.failure, error: e.toString()));
    }
  }

  Future<void> _onSendFeedback(SendFeedback event, Emitter<RecState> emit) async {
    emit(state.copyWith(status: RecStatus.loading));
    try {
      final pair = await api.sendFeedback(id: event.id, action: event.action);
      emit(state.copyWith(
        status: RecStatus.success,
        current: pair.$1,
        next: pair.$2,
      ));
    } catch (e) {
      emit(state.copyWith(status: RecStatus.failure, error: e.toString()));
    }
  }
}
