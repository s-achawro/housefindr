import 'dart:math';
import 'package:flutter/material.dart';
import 'house_user.dart';
import 'package:fluttertoast/fluttertoast.dart';

enum CardStatus {like, dislike, superLike }

class CardProvider extends ChangeNotifier{
  // List<String> _urlImages = [];
  List<HouseUser> _houses = [];
  bool _isDragging = false;
  double _angle = 0;
  Offset _position = Offset.zero;
  Size _screenSize = Size.zero;

  // List<String> get urlImages => _urlImages;
  List<HouseUser> get houses => _houses;
  bool get isDragging => _isDragging;
  Offset get position => _position;
  double get angle => _angle;

  CardProvider() {
    resetUsers();
  }

  void setScreenSize(Size screenSize) => _screenSize = screenSize;

  void startPosition(DragStartDetails details) {
    _isDragging = true;
    notifyListeners();
  }

  void updatePosition(DragUpdateDetails details) {
    _position += details.delta;

    final x = _position.dx;
    _angle = 45 * x / _screenSize.width;

    notifyListeners();
  }

  void endPosition() {
    _isDragging = false;
    notifyListeners();

    final status = getStatus(force: true);

    // if (status != null){
    //   Fluttertoast.cancel();
    //   Fluttertoast.showToast(
    //     msg: status.name,
    //     // toastLength: Toast.LENGTH_SHORT,
    //     gravity: ToastGravity.BOTTOM,
    //     timeInSecForIosWeb: 1,
    //     backgroundColor: const Color(0xCC000000),
    //     textColor: const Color(0xFFFFFFFF),
    //     fontSize: 30,
    //   );
    // }
    switch (status){
      case CardStatus.like:
        like();
        break;
      case CardStatus.dislike:
        dislike();
        break;
      case CardStatus.superLike:
        superLike();
        break;
      default:
        resetPosition();
    }
  }

  void resetPosition() {
    _isDragging = false;
    _position = Offset.zero;
    _angle = 0;

    notifyListeners();
  }

  double getStatusOpacity(){
    final delta = 100;
    final pos = max(_position.dx.abs(), _position.dy.abs());
    final opacity = pos / delta;

    return min(opacity,1);
  }

  CardStatus? getStatus({bool force = false}) {
    final x = _position.dx;
    final y = _position.dy;
    final forceSuperLike = x.abs() < 20;

    if (force) {
      final delta = _screenSize.width / 6;

      if (x >= delta) {
        return CardStatus.like;
      } else if (x <= -delta) {
        return CardStatus.dislike;
      } else if (y <= -delta / 2 && forceSuperLike) {
        return CardStatus.superLike;
      }
    }else {
      final delta = _screenSize.width / 13;

      if (y <= -delta * 2 && forceSuperLike){
        return CardStatus.superLike;
      }else if (x >= delta){
        return CardStatus.like;
      }else if (x <= -delta){
        return CardStatus.dislike;
      }
    }
    return null;
  }

  void dislike(){
    _angle = -20;
    _position -= Offset(2* _screenSize.width, 0);
    _nextCard();

    notifyListeners();
  }
  void like() {
    _angle = 20;
    _position += Offset(2 * _screenSize.width, 0);
    _nextCard();

    notifyListeners();
  }

  void superLike(){
    _angle = 0;
    _position -= Offset(0, _screenSize.height);
    _nextCard();

    notifyListeners();
  }

  Future _nextCard() async {
    await Future.delayed(Duration(milliseconds: 200));
    _houses.removeLast();
    resetPosition();
  }

  void removeLast() {
  if (_houses.isEmpty) return;
  _houses.removeLast();
  _position = Offset.zero;
  _angle = 0;
  notifyListeners();
}


  void resetUsers() {
  //   _urlImages = <String>[
  //     'https://www.livehome3d.com/assets/img/articles/design-house/how-to-design-a-house.jpg',
  //     'https://www.houseplans.net/news/wp-content/uploads/2023/07/57260-768.jpeg',
  //     'https://hips.hearstapps.com/hmg-prod/images/dutch-colonial-house-style-66956274903da.jpg?crop=1.00xw:0.671xh;0,0.131xh&resize=1120:*',
  //     'https://usvintagewood.com/wp-content/uploads/2021/05/image1.jpg'
  //   ].reversed.toList();
  //   notifyListeners();
  // }
    _houses = <HouseUser>[
      const HouseUser(
        number: '2 bathrooms \n4 bedrooms',
        address: '\nRedwood Ln, Santa Cruz\n',
        imageUrl: 'https://www.livehome3d.com/assets/img/articles/design-house/how-to-design-a-house.jpg',
      ),
      const HouseUser(
        number: '57260',
        address: 'Oak Ridge Dr, Austin',
        imageUrl: 'https://www.houseplans.net/news/wp-content/uploads/2023/07/57260-768.jpeg',
      ),
      const HouseUser(
        number: '88',
        address: 'Maple Ave, Boston',
        imageUrl: 'https://hips.hearstapps.com/hmg-prod/images/dutch-colonial-house-style-66956274903da.jpg?crop=1.00xw:0.671xh;0,0.131xh&resize=1120:*',
      ),
      const HouseUser(
        number: '2 bathrooms \n 4 bedrooms',
        address: '\nRedwood Ln, Santa Cruz',
        imageUrl: 'https://usvintagewood.com/wp-content/uploads/2021/05/image1.jpg',
      ),
    ].reversed.toList();

    _position = Offset.zero;
    _angle = 0;
    notifyListeners();
  }
}