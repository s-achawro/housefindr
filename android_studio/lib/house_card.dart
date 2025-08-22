import 'dart:math';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'card_provider.dart';


class HouseCard extends StatefulWidget {
  final String urlImage;
  final bool isFront;

  const HouseCard({
    super.key,
    required this.urlImage,
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
            child: buildCard(),
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
          image: DecorationImage(
            image: NetworkImage(widget.urlImage),
            fit: BoxFit.cover,
            //   fit: BoxFit.contain,
            alignment: Alignment(-0.3, 0),
          ),
        ),
      ),
    );
  }
