import 'dart:math';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'card_provider.dart';
import 'house_user.dart';

class HouseCard extends StatefulWidget {
  // final String urlImage;
  final HouseUser house;
  final bool isFront;

  const HouseCard({
    super.key,
    // required this.urlImage,
    required this.house,
    required this.isFront,
  });

  @override
  State<HouseCard> createState() => _HouseCardState();
}

// outside HouseCard
class _HouseCardState extends State<HouseCard> {
  @override
  void initState() {
    super.initState();

    // read screen size for swiping
    WidgetsBinding.instance!.addPostFrameCallback((_){
      final size = MediaQuery.of(context).size;

      final provider = Provider.of<CardProvider>(context, listen: false);
      provider.setScreenSize(size);
    });
  }

  @override
  Widget build(BuildContext context) => SizedBox.expand(
      child: widget.isFront ? buildFrontCard() : buildCard(),
    );


  Widget buildFrontCard() => GestureDetector(
    child: LayoutBuilder(
      builder: (context, constraints){
        final provider = Provider.of<CardProvider>(context);
        final position = provider.position;
        final milliseconds = provider.isDragging ? 0 : 400;

        final center = constraints.smallest.center(Offset.zero);
        final angle = provider.angle * pi / 180;
        final rotateMatrix = Matrix4.identity()
          ..translate(center.dx, center.dy)
          ..rotateZ(angle)
          ..translate(-center.dx, -center.dy);

        return AnimatedContainer(
          curve: Curves.easeInOut,
            duration: Duration(milliseconds: milliseconds),
            transform: rotateMatrix
              ..translate(position.dx, position.dy),
            child: Stack(
              children:[
                buildCard(),
                buildStamps(),
          ],
            ),
        );
      },
    ),
    onPanStart: (details){
      final provider = Provider.of<CardProvider>(context, listen:false);

      provider.startPosition(details);
    },
    onPanUpdate: (details){
      final provider = Provider.of<CardProvider>(context,listen:false);

      provider.updatePosition(details);
    },
    onPanEnd: (details){
      final provider = Provider.of<CardProvider>(context,listen:false);

      provider.endPosition();
    },
  );

  Widget buildCard() => ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: Container(
        decoration: BoxDecoration(
          // color: Colors.grey.shade200,
          color: Color(0xFFE7E0D4),
          image: DecorationImage(
            image: NetworkImage(widget.house.imageUrl),
            // fit: BoxFit.cover,
              fit: BoxFit.contain,
            alignment: Alignment(-0.3, 0),
          ),
        ),
        child: Container(
          padding: EdgeInsets.all(20),
          child: Column(
            children: [
              buildName(),
          ],
          ),
        ),
        )
      );

  Widget buildName() => Row(
    children: [
      Text(
      widget.house.number,
      style: TextStyle(
        fontSize: 15,
        color: Colors.black,
        fontWeight: FontWeight.bold,
      ),
      ),
    const SizedBox(width: 16),
    Text(
      '${widget.house.address}',
      style: TextStyle(
        fontSize: 15,
        color: Colors.black,
      ),
    ),
    ],
  );


  Widget buildStamps(){
    final provider = Provider.of<CardProvider>(context);
    final status = provider.getStatus();
    final opacity = provider.getStatusOpacity();

    switch (status) {
      case CardStatus.like:
        final child = buildStamp(
            angle: -0.5,
            color: Colors.green,
            text: 'LIKE',
            opacity: opacity,
          );
        return Positioned(top: 64, left: 50, child: child);

      case CardStatus.dislike:
        final child = buildStamp(
            angle:0.5,
            color: Colors.red,
            text: 'NOPE',
            opacity: opacity,
          );
        return Positioned(top:64, left:180, child: child);

      case CardStatus.superLike:
        final child = Center(
          child: buildStamp(
              color: Colors.blue,
              text: 'SUPER\nLIKE',
              opacity: opacity,
          ),
        );
          return Positioned(
              bottom: 128,
              right:0,
              left: 0,
              child: child
          );

        default:
          return Container();
    }
  }

  Widget buildStamp({
    double angle = 0,
    required Color color,
    required String text,
    required double opacity,
  })  {
    return Opacity(
      opacity: opacity,
      child: Transform.rotate(
        angle: angle,
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: 8),
          decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color, width:4),
        ),
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: TextStyle(
            color: color,
            fontSize: 48,
            fontWeight: FontWeight.bold,
          ),
        )
        ),
    ),
    );
  }
  }

