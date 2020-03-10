/*
 * Copyright 2019 Google
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#import "FIRAuthRPCRequest.h"
#import "FIRIdentityToolkitRequest.h"
#import "FIRAuthProtoFinalizeMfaPhoneRequestInfo.h"

NS_ASSUME_NONNULL_BEGIN

@interface FIRFinalizeMfaSignInRequest : FIRIdentityToolkitRequest <FIRAuthRPCRequest>

@property(nonatomic, copy, readonly, nullable) NSString *MFAProvider;

@property(nonatomic, copy, readonly, nullable) NSString *MFAPendingCredential;

@property(nonatomic, copy, readonly, nullable) FIRAuthProtoFinalizeMfaPhoneRequestInfo *verificationInfo;

- (nullable instancetype)initWithMfaProvider:(NSString *)MFAProvider
                        MFAPendingCredential:(NSString *)MFAPendingCredential
                            verificationInfo:(FIRAuthProtoFinalizeMfaPhoneRequestInfo *)verificationInfo
                        requestConfiguration:(FIRAuthRequestConfiguration *)requestConfiguration;

@end

NS_ASSUME_NONNULL_END
