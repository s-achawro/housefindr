class HouseUser {
  final String id;
  final String number;
  final String address;
  final String imageUrl;

  const HouseUser({
    required this.id,
    required this.number,
    required this.address,
    required this.imageUrl,
});

  // Helper to build from backend JSON
  factory HouseUser.fromListing(Map<String, dynamic> j) {
    final beds  = j['beds'] ?? 0;
    final baths = j['baths'] ?? 0;
    final city  = (j['city'] ?? '').toString();
    return HouseUser(
      id: (j['id'] ?? '').toString(),
      number: '$baths bathrooms \n$beds bedrooms',
      address: city.isEmpty ? 'Unknown' : city,
      // Use a real image if your API returns one; else a placeholder:
      imageUrl: 'https://picsum.photos/seed/${j['id']}/800/600',
    );
  }
}
