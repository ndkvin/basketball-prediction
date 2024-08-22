import base64
import binascii

def encode(data):
    # Encode the data to Base64
    first_encode = base64.b64encode(data.encode('utf-8'))
    # Encode the already Base64-encoded data again
    double_encoded = base64.b64encode(first_encode)
    return double_encoded.decode('utf-8')

def decode(encoded_data):
    try:
        # Decode the Base64-encoded data twice
        first_decode = base64.b64decode(encoded_data)
        final_decode = base64.b64decode(first_decode)
        return final_decode.decode('utf-8')
    except (binascii.Error, ValueError) as e:
        print(f"Decoding error: {e}")
        return None

# # Example usage
# data = "example2024-08-15 21:12:53"

# # Double Base64 encode the data
# encoded_data = encode(data)
# print(f"Double Encoded Data: {encoded_data}")
