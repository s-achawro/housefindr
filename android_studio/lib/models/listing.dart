// lib/models/listing.dart
class Listing {
  final String id;
  final String? address;        // may be null
  final num? price;
  final num? sqft;
  final int? beds;
  final num? baths;
  final String? city;
  final String? style;
  final String? listingType;
  final String? tenure;
  final String? imageUrl;


  Listing({
    required this.id,
    this.address,
    this.price,
    this.sqft,
    this.beds,
    this.baths,
    this.city,
    this.style,
    this.listingType,
    this.tenure,
    this.imageUrl,
  });

  factory Listing.fromJson(Map<String, dynamic>? j) {
    if (j == null) return Listing(id: "");
    return Listing(
      id: (j["id"] ?? "").toString(),
      address: j["address"] as String?,
      price: _toNum(j["price"]),
      sqft: _toNum(j["sqft"]),
      beds: _toInt(j["beds"]),
      baths: _toNum(j["baths"]),
      city: j["city"] as String?,
      style: j["style"] as String?,
      listingType: j["listing_type"] as String?,
      tenure: j["tenure"] as String?,
      imageUrl: j["image_url"] as String?,
    );
  }

  static num? _toNum(dynamic v) {
    if (v == null) return null;
    if (v is num) return v;
    return num.tryParse(v.toString());
  }

  static int? _toInt(dynamic v) {
    if (v == null) return null;
    if (v is int) return v;
    return int.tryParse(v.toString());
  }
}