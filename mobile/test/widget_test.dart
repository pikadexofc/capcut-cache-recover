import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:export_capcut_mobile/core/bdve_cryptor.dart';
import 'package:export_capcut_mobile/main.dart';

void main() {
  group('BdveCryptor unit tests', () {
    test('deriveKey returns candidate key from obfuscated header', () {
      final header = Uint8List.fromList([0x3B, 0x3B, 0x3B, 0x00, 0x5D, 0x74, 0x79, 0x70]);
      final key = BdveCryptor.deriveKey(header);
      expect(key, 0x3B);
    });

    test('decryptBytes reverses XOR stream accurately', () {
      final plain = Uint8List.fromList([0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70]);
      final encrypted = Uint8List(plain.length + 68);
      for (int i = 0; i < plain.length; i++) {
        encrypted[i] = plain[i] ^ 0x3B;
      }
      final params = CryptorParams(key: 0x3B, step: 100, length: 100);
      final decrypted = BdveCryptor.decryptBytes(encrypted, params);
      expect(decrypted, plain);
    });
  });

  testWidgets('ExportCapcutApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ExportCapcutApp());
    expect(find.text('Export Capcut Pro Video Free'), findsWidgets);
  });
}
