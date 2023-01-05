import json
import base64
from authlib.jose import jwt
import re
from datetime import datetime
import pytz


SUFFIX = "IPD"

def rightnow_str():
  bkkTime = pytz.timezone("Asia/Bangkok") 
  rn_str_tmp  = datetime.now(bkkTime)
  rn_str = rn_str_tmp.strftime("%Y-%m-%dT%H:%M:%S+07:00")
  # print(rn_str)
  return rn_str

def rightnow_forfile():
  bkkTime = pytz.timezone("Asia/Bangkok") 
  rn_str_tmp  = datetime.now(bkkTime)
  rn_str = rn_str_tmp.strftime("%Y%m%dT%H%M%S%f")
  return rn_str


def signFhirMessage(PRIVATE_KEY, PUBLIC_KEY,  INPUT_FILE_NAME, sigType , sigData):

  with open(INPUT_FILE_NAME, 'r',  encoding='utf-8') as f:
    # Load the JSON data from the file
    data = json.load(f)
  

  # Load Privatekey 
  file1 = open(PRIVATE_KEY, 'r')
  key = file1.read()

  # Load Publickey 
  file2 = open(PUBLIC_KEY, 'r')
  pub = file2.read()


  tmp1 = pub.replace("-----BEGIN CERTIFICATE-----\n","") 
  tmp2 = tmp1.replace("-----END CERTIFICATE-----","") 
  min_pub = tmp2.replace("\n","")


  header = {
    "alg": "RS256",
    "typ": "JWT",
    "x5c" : []
  }

  header["x5c"].append(min_pub)
  # header

  # Load Privatekey 
  file1 = open(PRIVATE_KEY, 'r')
  key = file1.read()

  # Load Publickey 
  file2 = open(PUBLIC_KEY, 'r')
  pub = file2.read()

  # Sign data as JWT 

  jwt1 = jwt.encode(header, data, key)
  jwt1_text = jwt1.decode("utf-8")

#   print(f"{jwt1_text}")

  # jws แบบ base64 encoded
  #base64 [base64url(header) .  .  signature ]

  #modify jwt1

  jwt1_spt = jwt1_text.split(".")

  #inject new_payload

  jws1 = f"{jwt1_spt[0]}..{jwt1_spt[2]}"

  jws1_base64 = base64.b64encode(jws1.encode("ascii"))

  jws1_base64_text = jws1_base64.decode("utf-8")
  # jws1_base64_text

  filePrefix  = ""
  if sigType == "provenance" :
    
    # add base64 to provenanace 
    sigData["resource"]["signature"][0]["data"] = jws1_base64_text
    # append provenance to main data
    data["entry"].append(sigData)
    filePrefix = "doctor_signed"

  elif sigType == "signature" :
    # add base64 to Signature.data 
    sigData["data"] = jws1_base64_text
    data["signature"] = sigData
    filePrefix = "hospital_signed"
    

  #*** Serializing json  
  #*** https://phyblas.hinaboshi.com/20190427
  #*** https://stackpython.co/tutorial/json-python

  # result = json.dumps(data, ensure_ascii=False)
  # print(result)

  filetime = rightnow_forfile()

  OUTPUT_FILE_NAME = f"{filetime}_{filePrefix}_output.json"

  print(f"OUTPUT FILENAME IS : {OUTPUT_FILE_NAME}")

  with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as json_output:
    json.dump(data, json_output, ensure_ascii=False )
  return OUTPUT_FILE_NAME



#=============================================================
#
#   DOCTOR SIGN
#
#=============================================================


DOC_PRIVATE_KEY = "test_doc_private_key.pem"
DOC_PUBLIC_KEY  = "test_doc_public_key.pem"
DOC_INPUT_FILE_NAME = "20221219T131744798620_MedicalCertificate.json"
# ชื่อไฟล์ output จะไปปรากฏใน google drive 
# DOC_OUTPUT_FILE_NAME = f"{prefix_output}MCDL_OUTPUT_dr_signed.json"

timetosign = rightnow_str()
# timetosign
provenance_doc_MCSL = {
            "fullUrl": "Provenance/10",
            "resource": {
                "resourceType": "Provenance",
                "id": "10",
                "meta": {
                    "profile": ["http://fhir/StructureDefinition/MCSLProvenancePractitionerProfile"]
                },
                "target": [
                    {
                        "reference": "Composition/1",
                        "type": "Composition"
                    }
                ],
                "recorded": f"{timetosign}",
                "agent": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                                    "code": "author",
                                    "display": "Author"
                                }
                            ]
                        },
                        "who": {"reference": "Practitioner/4"}
                    }
                ],
                "signature": [
                    {
                        "type": [
                            {
                                "system": "urn:iso-astm:E1762-95:2013",
                                "code": "1.2.840.10065.1.12.1.1",
                                "display": "Author's Signature"
                            }
                        ],
                        "when": f"{timetosign}",
                        "who": {"reference": "Practitioner/4"},
                        "targetFormat": "json",
                        "sigFormat": "application/jose",
                        "data": ""
                    }
                ]
            }
        }

provenance_doc_MCLD = {
            "fullUrl": "Provenance/13",
            "resource": {
                "resourceType": "Provenance",
                "id": "13",
                "meta": {
                    "profile": ["https://schemas.teda.th/teda/teda-affiliate/the-medical-council-of-thailand/medical-certificate-for-driving-license/-/raw/main/StructureDefinition/MCDLProvenancePractitionerProfile"]
                },
                "target": [
                    {
                        "reference": "Condition/7",
                        "type": "Condition"
                    }
                ],
                "recorded": f"{timetosign}",
                "agent": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                                    "code": "author",
                                    "display": "Author"
                                }
                            ]
                        },
                        "who": {"reference": "Practitioner/6"}
                    }
                ],
                "signature": [
                    {
                        "type": [
                            {
                                "system": "urn:iso-astm:E1762-95:2013",
                                "code": "1.2.840.10065.1.12.1.1",
                                "display": "Author's Signature"
                            }
                        ],
                        "when": f"{timetosign}",
                        "who": {"reference": "Practitioner/6"},
                        "targetFormat": "json",
                        "sigFormat": "application/jose",
                        "data": ""
                    }
                ]
            }
        }



provenance_doc_MC = {
            "fullUrl": "Provenance/13",
            "resource": {
                "resourceType": "Provenance",
                "id": "13",
                "meta": {
                    "profile": ["http://fhir/StructureDefinition/MCProvenancePractitionerProfile"]
                },
                "target": [
                    {
                        "reference": "Condition/7",
                        "type": "Condition"
                    }
                ],
                "recorded": f"{timetosign}",
                "agent": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                                    "code": "author",
                                    "display": "Author"
                                }
                            ]
                        },
                        "who": {"reference": "Practitioner/6"}
                    }
                ],
                "signature": [
                    {
                        "type": [
                            {
                                "system": "urn:iso-astm:E1762-95:2013",
                                "code": "1.2.840.10065.1.12.1.1",
                                "display": "Author's Signature"
                            }
                        ],
                        "when": f"{timetosign}",
                        "who": {"reference": "Practitioner/6"},
                        "targetFormat": "json",
                        "sigFormat": "application/jose",
                        "data": "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0lzSW5nMVl5STZXeUpOU1VsSFpGUkRRMEpHTW1kQmQwbENRV2RKU1V3d1pFRldVMWxoZFdoemQwUlJXVXBMYjFwSmFIWmpUa0ZSUlV4Q1VVRjNXV3BGVEUxQmEwZEJNVlZGUW1oTlExWkZaM2hOZWtGNFFtZE9Wa0pCYjAxTGExWnpXbGRPTUdOdE9YVmhWMDFuVmtoS2FHSnVUbWhaTTFKd1lqSTFla2xGVW14a2JWWnpZak5DZEZwWE5UQkpSVVp1V2xjMWFtVlVSV1ZOUW5kSFFURlZSVUYzZDFaU1ZsSkZVVk5DU21KdVVteGpiVFZvWWtOQ1JGRlRRWFJKUldONVRVSTBXRVJVU1hsTlJHdDNUVlJCTkUxNlJURk5NVzlZUkZSSk1FMUVaM3BOVkVFMFRYcEZNVTB4YjNkblowVkhUVkZ6ZDBOUldVUldVVkZIUlhkS1ZWTkVSWGxOUkVGSFFURlZSVU5uZDNBMFRHMURORXhwYWpSTWFVZzBUR2xsTkV4cGFUUk1hWGswVEdsaE5FeHBlVFJNYVd4SlQwTTBjWFZETkc1MVF6UnRUME0wY2xNMGVFNXFRVEJDWjA1V1FrRnpUVXhsUXpSeFQwTTBkV1ZETkcxbFF6UnZkVU0xYWs5RE5HeGxRelJ2SzBNMGNDdEROR2xQUXpSeGRVTTBkVTlETkdkMVF6UnZUME0wYzNWRE5HNXFSVzVOUTFWSFFURlZSVVJCZDJVMFRHbDBORXhwZVRSTWFXazBUR2swTkV4cGFqUk1iVUkwVEdsbE5FeHBXRFJNYVdrMFRHMU5UVkU0ZDBSUldVUldVVkZGUkVGYVUxbFhkR3RhVjFWNFJVUkJUMEpuVGxaQ1EyOU5RakZPZG1KWFRtOVpWMnQ0UkdwQlRVSm5UbFpDUVZWVVFsUkZlVTE2VVRGTlV6aDNURkZaUkZaUlVVUkVRMkpuZFV0eVozVkxTR2QxU1hKbmRVeE1aM1ZMU1djMFRHbHFORXhwZURSTWFVSTBUR2xWTkV4cE1VbERhRlZhV0U0d1MxUkRRMEZUU1hkRVVWbEtTMjlhU1doMlkwNUJVVVZDUWxGQlJHZG5SVkJCUkVORFFWRnZRMmRuUlVKQlRVRnRMMUpOTUM4eGJFaFVaRUl2WlhkNGNsSXJhSEY1Y0N0elptOTNOV2d5Vm1aR1VHMUhhWHBRYjFOQlNtbHNOSEJGYUNzd1JuSldhekpoZDBrclVEZDBLelJKZDB4Q1RtVXdaaXR3UWxaTVVITndMMUJVY2xGd1dGSjFOa295VEM4Mk4yUnpXa2xHTTFGRmR6Vm5kMlpqYVV0TU9HRlhaVE5NUmlzdmNFdFlVMHhIV1ZZNFFrdHplRTFPWTBrdmFEQTBOMWN3YW1oRVVtaDNXWGczUjNaU1JDdExVSEl5Y0dsYWVWcHlVRXB2ZVdwbmJsYzBXbGt3TVZWcldrb3JRbVptYlZnNGJtY3ZOVlZIVjNWb05uQnFaVFZ3VHpSVVlXSkdOREp6WVVOVE9HTkJiM05DVUVvNGREUXdNbU16TkVwa01rSndhMjAzTjBkWWRHTlBNeTl4YUc1TWJtOXpiWFJXSzA5U1RGQklVMGwwUkU5SVVXRkhjbVZCUzJ0NWVqTTVWVlJtU1VSMFJWcE9la1ZIWTNkUmNXeE5iSFZMTDJodVpGZENUaXNyTXpGYWRuRmtNR1V2TURCaGEwazJUR3QxSzBKalEwRjNSVUZCWVU5RFFWbGpkMmRuUjBSTlNITkhRME56UjBGUlZVWkNkMFZDUWtjNGQySlVRVFZDWjJkeVFtZEZSa0pSWTNkQmIxbDBZVWhTTUdORWIzWk1NMHBzWTBjNGRWcFlVbXRaVXpWMlkyazFNR0ZET1d4a1IxSm9ZVmMxTUZreVJtNU5hVFZxV1ZkT2JHTnVVWFZaTTBvd1RVUkJSME5EYzBkQlVWVkdRbnBCUW1ocFVtOWtTRkozVDJrNGRtTnRWbmRpZVRWc1pFZFNhRXh0T1hsTWJsSnZUREpXTUZwSFJuQmlibEp1VFcwNWFtTXpRWGRJVVZsRVZsSXdUMEpDV1VWR1NGWndObVJVU1VOMlNtNXZaMkZRU3pGNWVuVTBkMk5DYkZkelRVRjNSMEV4VldSRmQwVkNMM2RSUTAxQlFYZElkMWxFVmxJd2FrSkNaM2RHYjBGVkswaDNTRzgxYVRGblJsY3JWbXhKYlRsU1pGcDJObUV4T0RCcmQxRlJXVVJXVWpCblFrUnZkMDlFUVRKQ1oxcG5hRmgzUWtGUlJYZE1SRUZ4UW1kbmNrSm5SVVpDVVdORFFWSlpaV0ZJVWpCalJHOTJUREkxZVZreVJYVmFNamgxWkVkbmRtTklWbWxpUjJ4NllVTTFiMlJITVhOTlJEQkhRVEZWWkVoM1VUSk5SRkYzVFhGQmQyOUROa2RNUjJnd1pFaEJOa3g1T1hsYVdFSjJURzFXTUZwSFJYVmlNMGwxWkVkbmRsSldVa1ZSVld4MVpFZFdlV0p0Um5OWk1rVjBXbnBKZFZrelNuTk5RVFJIUVRGVlpFUjNSVUl2ZDFGRlFYZEpSalJFUVd0Q1owNVdTRkpGUlVoVVFXSm5VbXg2WWpJeGFtRkhSbkJSUjFZd1drZEZkR0ZIT1hwalIyd3dXVmQzZFZreU9YUk5RVEJIUTFOeFIxTkpZak5FVVVWQ1EzZFZRVUUwU1VOQlVVSldNbUU1VEVOMUwyWndjbTl6YlcxRWRVRXJUM0I1TVhWb1RIaEdkR1pKYTI1RU1YZFlVamRuSzNBNVVUUk1UV1JVTDB4alNqbDNjM1pJUm5welJWZ3dUbXBOUmpRelNISnRjVmhQU1haUlFsWnVLMjVtYlhVeWNubG1hME14UW05NlEyNUNaamhRYW1GVlpWWmlTWGM0WkRaVVdqazJSV2QyVGsxelJVTm5aSFV2VHk5T1FuRlpibkpWUlVNeFpFMHhVMVpuZVZCaVFYVjNUR1pPVkcxSVUzbDNZelpvVUZsaFQzWlJaelJ4VTJnNVJqSkVPREpRU1dkaWVGVjBWalJsVFdOalNWcFhNM0F2TTNwcVdYVTBNekpxYkZOcU1VUlJjV0ZoTjBrek0wbElkVkJxYjNkRFJrSm9ZelJMVWl0T1dqWlpSMHBGTDNWMGNURnZWRzF3WkhsVE0zaHlLM0pSVEZCaWVrUjZSeXRJYXpkaFpWUlFhMEYxTDNoaVJXOVNVVlJSZUU5U2JEQkdUR1J1WnpVMlRqSkdNVU5FZUZNMmNVODBVR05YZWsxb1lYcGtWVUV3Y1RaMGJuY3hNWE5ST0VoaFRERjBPR0o1UTFGcE5IWndjVlp2UnpOcGVFaEZSMDl2TnpFMFIwaHdWMmRxZG1KNFJYUlNaSEk0UTFNcmREVnJNVXRHY1dOTldXOVJXR2MyVEVveGNVMXhlWGwwTXpWamMybDZPREJEZG5SV05FRmlVSGxRYkhWbGRteFNValpMVjNOdmVuVXhNazFDTVhwaVlWSjZRMEpFU1had04xSnNSRmMyY2xGSk9WQnlSbEV6YXpoNVptVm9XblZ5T0cxQ1MzUm5Sa0puWjJzemRERnVTVmxYTW10SmNXTTBaalZqY1RGMFQzVkJRMVJtWW1SQlVUUkdaVXRCYldwME1FaHllbW80WVZOeGRXTmFkMGxNUTFRMFZXRmFOMjExSzFJMWJrVm1TVFIzTDNKamJYSnFkMFEzVVc5NVYzYzNWRWxxYzBsU1lrbE5PVkJoVEZOdlMxQjNTR2RoU2xCSFNtMW9Va2N4VXpZMFdGZExXVmh0YWxOblRDdEJUVmQ1U0ROdmRqSkhOVlF3V1ZjeE4wMDJWbTlKVVdwVVFWWjFRVWtyTWtaVU1uVnNhVFZXVml0S2FFdHdNMUpSY0hsaldVZDRaVEF2Y21kRVVUMDlJbDE5Li5sWnVHRC10bHcwclFKeUpfMU5WcHIzTy00SDNRR3d1ZlRCQmFvZFRadFl0bGVmVkJ1T3BRZUlPbFVfNktBYzlLNlJRd0lfZnBXcWhJLWU3WjhvSk1BQ0NPOFNlSUdVdEdlSVFWOEN5Ty1sNE5JM0NqN0trejZEanYzMGpFanpDcWNZNm9KWXh2WVMyVUdtcVgxRVFTVnJ0enpHUmI2QTBJVDdCaTBXbWM0MUJPRjRJcG9mYk8yUmpNaDlZOUw3bldYTW1UYWlreDc5NG1XOWtwVVRBMDMzbDVNVURiN2RZalJPMFFBeUNsYTVKZ0p6VDNtbGYwRXVFZklMMS1JT0xqOGJ0R2VhN0VvQU5QYzhnMFMtczFuQXlUbWhIMXBlakZRN2FLZFFwdjFad1Vnc3J0LVgyZk4zX1dNT21zRTZBYTVjODBDWHVreWdBV1dtWjNwRTBwMVE="
                    }
                ]
            }
        }


provenance_doc = provenance_doc_MCSL
# DOC_INPUT_FILE_NAME = "20221129_CertificateofIllness_ER.json"

doc_signed_filename = signFhirMessage(DOC_PRIVATE_KEY, DOC_PUBLIC_KEY,  DOC_INPUT_FILE_NAME, "provenance" , provenance_doc)

#=============================================================
#
#   HOSPITAL SIGN
#
#=============================================================




HOSP_PRIVATE_KEY = "hospitaltest2_private.pem"
HOSP_PUBLIC_KEY  = "hospitaltest2_public.pem"
HOSP_INPUT_FILE_NAME = doc_signed_filename
# ชื่อไฟล์ output จะไปปรากฏใน google drive 
# HOSP_OUTPUT_FILE_NAME = f"{prefix_output}OUTPUT_HOSPITAL_signed.json"

timetosign = rightnow_str()

hospitalSignature_MCSL = {
        "type": [
            {
                "system": "urn:iso-astm:E1762-95:2013",
                "code": "1.2.840.10065.1.12.1.1",
                "display": "Author's Signature"
            }
        ],
        "when": f"{timetosign}",
        "who": {"reference": "Organization/7"},
        "targetFormat": "json",
        "sigFormat": "application/jose",
        "data": ""
    }

hospitalSignature_MC = {
        "type": [
            {
                "system": "urn:iso-astm:E1762-95:2013",
                "code": "1.2.840.10065.1.12.1.1",
                "display": "Author's Signature"
            }
        ],
        "when": f"{timetosign}",
        "who": {"reference": "Organization/10"},
        "targetFormat": "json",
        "sigFormat": "application/jose",
        "data": ""
    }

hospitalSignature_MCDL = {
        "type": [
            {
                "system": "urn:iso-astm:E1762-95:2013",
                "code": "1.2.840.10065.1.12.1.1",
                "display": "Author's Signature"
            }
        ],
        "when": f"{timetosign}",
        "who": {"reference": "Organization/10"},
        "targetFormat": "json",
        "sigFormat": "application/jose",
        "data": ""
    }

hospitalSignature = hospitalSignature_MCSL
signFhirMessage(HOSP_PRIVATE_KEY, HOSP_PUBLIC_KEY,  HOSP_INPUT_FILE_NAME,  "signature" , hospitalSignature)