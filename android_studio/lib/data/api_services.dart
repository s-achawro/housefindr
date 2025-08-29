// lib/services/api_service.dart
import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform, SocketException;
import 'package:http/http.dart' as http;
import '../models/listing.dart';

class ApiService {
  static String get baseUrl =>
      Platform.isAndroid ? "http://10.0.2.2:5001" : "http://localhost:5001";

  Future<(Listing?, Listing?)> initFeed() async {
    try {
      final res = await http
          .get(Uri.parse("$baseUrl/init"))
          .timeout(const Duration(seconds: 8));

      if (res.statusCode != 200) {
        throw Exception("init failed: ${res.statusCode} ${res.body}");
      }
      final data = jsonDecode(res.body);
      return (Listing.fromJson(data["current"]), Listing.fromJson(data["next"]));
    } on TimeoutException {
      throw Exception("Timed out connecting to $baseUrl");
    } on SocketException catch (e) {
      throw Exception("Network error to $baseUrl: $e");
    }
  }

  Future<(Listing?, Listing?)> sendFeedback({
    required String id,
    required String action,
  }) async {
    try {
      final res = await http
          .post(
        Uri.parse("$baseUrl/feedback"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"id": id, "action": action}),
      )
          .timeout(const Duration(seconds: 8));

      if (res.statusCode != 200) {
        throw Exception("feedback failed: ${res.statusCode} ${res.body}");
      }
      final data = jsonDecode(res.body);
      return (Listing.fromJson(data["current"]), Listing.fromJson(data["next"]));
    } on TimeoutException {
      throw Exception("Timed out connecting to $baseUrl");
    } on SocketException catch (e) {
      throw Exception("Network error to $baseUrl: $e");
    }
  }

  Future<void> setConstraints({
    required Set<String> homeType,
    required Set<String> style,
    required String location,
    required int squareFeet,
    required int budget,
  }) async {
    final body = {
      "home_type": homeType.toList(),
      "style": style.toList(),
      "location": location,
      "square_feet": squareFeet,
      "budget": budget,
    };

    final res = await http
        .post(
      Uri.parse("${ApiService.baseUrl}/constraints"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    )
        .timeout(const Duration(seconds: 8));

    if (res.statusCode != 200) {
      throw Exception("setConstraints failed: ${res.statusCode} ${res.body}");
    }
  }
}

