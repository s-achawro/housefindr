import 'package:flutter/material.dart';
import 'house_card.dart'; // exports class HouseCard
import 'card_provider.dart';
import 'package:provider/provider.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) => ChangeNotifierProvider(
      create: (context) => CardProvider(),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Flutter Demo',
        theme: ThemeData(
        colorSchemeSeed: Colors.deepPurple,
        useMaterial3: true,
      ),
      home: const HomePage(),
    ),
  );
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text('HouseFindr'), backgroundColor: Color(0xFFE4D7C4),),
    body: SafeArea(
      child: Container(
        alignment: Alignment.center,
        padding: EdgeInsets.all(16),
        child: buildCards(context),
      ),
    ),
  );

  Widget buildCards(BuildContext context) {
      final provider = Provider.of<CardProvider>(context);
      // final urlImages = provider.urlImages;
      final houses = provider.houses;
      // return Stack(
      //   children: urlImages
      //       .map((urlImage) => HouseCard(
      //           urlImage: urlImage,
      //           isFront: urlImages.last == urlImage,
      //         ))
      //       .toList(),
      // );
    return Stack(
      children: houses
          .map((house) => HouseCard(
        house: house,
        isFront: house == houses.last,
      ))
          .toList(),
    );
  }
}

